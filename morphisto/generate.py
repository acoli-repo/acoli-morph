import os,sys,re,rdflib,traceback,argparse,subprocess,tempfile
import hashlib
from pprint import pprint

def parse_lfeats(lexinfo: str, output_type=dict):
        """ parse a sequence of ;-separated property-object statements, return a dict of arrays """
        if lexinfo==None or lexinfo.strip()=="":
            return {}
        lexinfo=re.sub(r"\s+"," ",lexinfo).strip()
        lexinfo=lexinfo.split(";")
        lexinfo=[ lfeat.strip() for lfeat in lexinfo ]
        lprop2vals={}
        for lfeat in set(lexinfo):
                        lfeat=lfeat.split(" ")
                        prop=lfeat[0]
                        vals=" ".join(lfeat[1:]).strip()
                        for val in vals.split(","):
                            val=val.strip()
                            if not prop in lprop2vals:
                                lprop2vals[prop] = [val]
                            elif not val in lprop2vals[prop]:
                                lprop2vals[prop].append(val)

        if output_type==dict:
            return lprop2vals
        if output_type==str:
            lprop2vals=[ prop+" "+", ".join(sorted(set(vals))) for prop,vals in lprop2vals.items() ]
            lprop2vals="; ".join(sorted(set(lprop2vals)))
            return lprop2vals

        raise(Exception("unsupported output_type \""+str(output_type)+", choose either str or dict"))


class Generator:

    def __init__(self, inflection_types, rule_extractor, annotation_model, tmpdir=tempfile.TemporaryDirectory(), skip_incomplete_forms=True, strict_mode=True):
        """ inflection_types OntoLex-Morph file with InflectionType definitions
            rule_extractor SPARQL script to produce transformation scripts from inflection_types, must be a SELECT statement that returns the variables ?itype and ?transform,
            this implementation of the generator further assumes that it produces a sed script
            if you provide a tmpdir, we re-use existing sed files
            """
        self.skip_incomplete_forms=skip_incomplete_forms
        self.tmpdir=tmpdir
        self.strict_mode=strict_mode

        #########
        # rules #
        #########

        itype2rules={}

        query=None

        with open(rule_extractor,"r") as input:
            query=input.read()
        flex=rdflib.Graph()
        flex.parse(inflection_types)

        qres = flex.query(query)
        nr=0
        for row in qres:
            if row.itype!=None and row.transformation!=None:
                itype=str(row.itype)
                transformation=str(row.transformation)
                if not itype in itype2rules:
                    itype2rules[itype] = [transformation]
                    nr+=1
                elif not transformation in itype2rules[itype]:
                    itype2rules[itype].append(transformation)
                    nr+=1

        print(rule_extractor+":",nr,"rules for",len(itype2rules),"paradigms")
        self.itype2rules=itype2rules

        ####################
        # annotation model #
        ####################

        concept2tags={}

        olia=rdflib.Graph()
        olia.parse(annotation_model)

        query = """
            PREFIX olias: <http://purl.org/olia/system.owl#>
            PREFIX lexinfo: <http://www.lexinfo.net/ontology/3.0/lexinfo#>

            SELECT distinct ?object ?tag_before ?tag_after ?lexinfo
                WHERE {
                    # object is anything that carries an olias:hasTag (etc.) property
                    # we do not permit olias:hasTagContaining or olias:hasTagMatching
                    # because there is no clear positioning information in them, they cannot be used to produce input symbols

                    { # if we just have the tag, we don't know if its at the beginning or the end, so we try both
                        ?object olias:hasTag ?tag_before.
                    } UNION {
                        ?object olias:hasTag ?tag_after.
                    } UNION {
                        ?object olias:hasTagStartingWith ?tag_before; olias:hasTagEndingWith ?tag_after
                    } UNION {
                        # if we have both starting with and ending specified, we assume that both need to apply (logical and)
                        # we do not allow them to be bound in isolation
                        ?object olias:hasTagStartingWith ?tag_before. MINUS { ?object olias:hasTagEndingWith [] }
                    } UNION {
                        ?object olias:hasTagEndingWith ?tag_after. MINUS { ?object olias:hasTagStartingWith [] }
                    } UNION {
                        # there may be tag-less elements, but then we require them to have a lexinfo POS
                        ?object lexinfo:partOfSpeech [].
                        MINUS { ?object olias:hasTag|olias:hasTagStartingWith|olias:hasTagEndingWith [] }
                    }

                    OPTIONAL {
                        ?object lexinfo:partOfSpeech [].
                        { SELECT ?object (GROUP_CONCAT(distinct ?lexfeat; separator="; ") as ?lexinfo)
                         WHERE {
                            ?object lexinfo:partOfSpeech [].
                            ?object ?prop ?val.
                            FILTER(contains(str(?prop),"lexinfo"))
                            #BIND(concat(str(?prop)," ",str(?val)) as ?lexfeat)
                            bind(if(isliteral(?val),
                                concat("<",str(?prop),'> "',str(?val),'"'),
                                concat("<",str(?prop),"> <",str(?val),">")
                                ) as ?lexfeat)
                        } GROUP BY ?object ?lexinfo
                        }
                    }
                }
            """

        qres = olia.query(query)
        for row in qres:
            row=["<"+str(row.object)+">",row.tag_before, row.tag_after, row.lexinfo ]
            row=[str(val) if val!=None else "" for val in row ]
            if row[0] in concept2tags:
                concept2tags[row[0]].append(tuple(row[1:]))
            else:
                concept2tags[row[0]]=[tuple(row[1:])]

        print(annotation_model+":",len(concept2tags),"annotation concepts",)
        self.concept2tags=concept2tags


    def generate(self, baseform, itype, lexinfo=None, concepts=None,skip_incomplete_forms=None, strict_mode=None):
        """ return dictionary of form -> features
            concept is a candidate concept from OLiA, empty => any
            lexinfo is a string of ;-separated lexinfo properties and values
            that describe the (lexical entry of the) base form
            with strictMode, we require that the entry features and the tag features overlap (and we generate only if entry provides features)
        """
        itype2rules=self.itype2rules
        concept2tags=self.concept2tags
        if skip_incomplete_forms==None:
            skip_incomplete_forms=self.skip_incomplete_forms
        if strict_mode==None:
            strict_mode=self.strict_mode

        if not itype in itype2rules:
            raise Exception("did not find paradigm (inflection type) \""+itype+"\"")

        if concepts==None or len(concepts)==0:
            concepts=concept2tags.keys()

        lexinfo=parse_lfeats(lexinfo)
        if len(lexinfo)==0 and strict_mode:
            raise Exception("no lexinfo features given, revise or run with strict_mode=False")
        result={}
        input2feats={}
        for concept in concepts:
            for left, right, tag_feats in concept2tags[concept]:
                compatible=True
                overlap=False
                tag_feats=parse_lfeats(tag_feats)
                for prop in lexinfo:
                    if prop in tag_feats:
                        overlap=True
                        vals=[ val for val in lexinfo[prop] if val in tag_feats[prop] ]
                        if len(vals)==0:
                            compatible=False
                            break;
                        else:
                            tag_feats[prop] = vals
                if len(tag_feats)>1 and strict_mode and not overlap:
                    return {}
                if compatible:
                    #print(tag_feats)
                    tag_feats = { prop : ", ".join(sorted(vals)) for prop,vals in tag_feats.items() }
                    tag_feats = [ prop+" "+vals for (prop,vals) in tag_feats.items() ]
                    tag_feats= "; ".join(sorted(tag_feats))
                    #print(tag_feats)
                    input=left+baseform+right
                    if not input in input2feats:
                        input2feats[input]=[tag_feats]
                    elif not tag_feats in input2feats[input]:
                        input2feats[input].append(feats)
        for input in input2feats:
            for rule in itype2rules[itype]:
                output=self._generate(rule,input)
                if not skip_incomplete_forms or not output.startswith("*"):
                    if not output in result:
                        result[output]=input2feats[input]
                    else:
                        result[output]+=input2feats[input]

        result = { output: sorted(set(feats)) for (output, feats) in result.items() }

        # some pruning: if the same form occurs both with more and fewer features, drop the version with fewer features
        pruned={}
        for form in result:
            if not form.startswith("*") or form[1:] != re.sub(r"<[^>]*>","",baseform):
                # we return hypothetical forms only if different from the basef
                tags=[]
                for t in result[form]:
                    skip=False
                    if t=="" and len(tags)>1:
                        skip=True
                    else:
                        for u in result[form]:
                            if t!=u and t in u:
                                skip=True
                                break
                        if not skip:
                            tterms=" ".join(t.split(","))
                            tterms=" ".join(t.split(";"))
                            for u in result[form]:
                                if u!=t and not skip:
                                    skip==True
                                    for tterm in tterms.split(" "):
                                        if not tterm in u:
                                            skip==False
                                            break
                    if not skip:
                        tags.append(t)
                pruned[form]=tags


        return pruned

    hash2replacements={}

    def _generate(self,sed_script,input):
        result=""
        error=""
        hash=hashlib.md5(sed_script.encode('utf-8')).hexdigest()

        if not hash in self.hash2replacements:
            replacements=sed_script.split(";")
            replacements=[ repl.strip().split("/") for repl in replacements ]
            replacements=[ (repl[1],repl[2]) for repl in replacements if len(repl)>2 ]

            sed2py={
                "\\u005e" : "\\^",
                "\\u002f" : "/",
                "\\u0022" : '\\"',
                "\\u0024" : "$",
                "\\u0026" : "&",
                "\\(": "(",
                "\\)": ")"
            }

            for n,(src,tgt) in enumerate(replacements):
                for sed,py in sed2py.items():
                    if sed in src:
                        src=py.join(src.split(sed))
                    if sed in tgt:
                        tgt=py.join(src.split(tgt))
                replacements[n]=(src,tgt)
            # print(replacements)
            self.hash2replacements[hash] = replacements

        output=input
        for src, tgt in self.hash2replacements[hash]:
            if output.endswith("$"): # not sure why this is happening, something in the sed2python transition and the escaping in regexpes
                output=output[0:-1]
            output=re.sub(src,tgt,output)
            if output.endswith("$"):
                output=output[0:-1]
        output=output.strip()
        if output.startswith("\*"):
            output=output[1:]

        return output.strip()

    def generate_for_dict(self, inputsource, skip_incomplete_forms=None,strict_mode=None, output_file=None, compact=False):
        """ given an OntoLex resource with paradigm/inflection type annotations,
            generate all hyppthetical inflected forms
            at the moment, this is for debugging only, so we just print to stdout
            if output_file==None, we write human-readable output to stdout
            otherwise, we write OntoLex data into this file
            if compact==True, we lump all features together, if compact==False, we consider each combination of features a separate form
        """

        if skip_incomplete_forms==None:
            skip_incomplete_forms=self.skip_incomplete_forms
        if strict_mode==None:
            strict_mode=self.strict_mode
        if output_file!=None:
            output_file=open(output_file,"wt")
            output_file.write("""
            PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
            PREFIX morph: <http://www.w3.org/ns/lemon/morph#>
            """)

        itype2rules=self.itype2rules
        concept2tags=self.concept2tags

        lex=rdflib.Graph()
        lex.parse(inputsource)

        entries_with_baseform=[]
        query = """
            PREFIX ontolex: <http://www.w3.org/ns/lemon/ontolex#>
            PREFIX morph: <http://www.w3.org/ns/lemon/morph#>
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX owl: <http://www.w3.org/2002/07/owl#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT distinct ?entry ?baseform ?lexinfo ?itype
            WHERE {

                # entries
                ?entry a ontolex:LexicalEntry.

                # itype
                ?entry morph:paradigm/morph:isParadigmOf ?itype.
                MINUS { ?itype a ontolex:LexicalEntry }
                # it is VERY unfortunate that these properties have the same name
                # we cannot reliably disambiguate them unless we (redundantly) declare the itypes as InflectionType in the lexicon data

                # baseform, if not provided, then canonical form
                {   # use canonicalForm iff no baseForm is specified
                    ?entry morph:baseForm/ontolex:writtenRep ?baseform
                } UNION {
                    ?entry morph:canonicalForm/ontolex:writtenRep ?baseform.
                    MINUS { ?entry morph:baseForm [] }
                }

                # lexinfo feats, if any
                     OPTIONAL {
                         ?entry lexinfo:partOfSpeech [].
                         { SELECT ?entry (GROUP_CONCAT(distinct ?lexfeat; separator="; ") as ?lexinfo)
                          WHERE {
                             ?entry lexinfo:partOfSpeech [].
                             ?entry ?prop ?val.
                             FILTER(contains(str(?prop),"lexinfo"))
                             #BIND(concat(str(?prop)," ",str(?val)) as ?lexfeat)
                             bind(if(isliteral(?val),
                                 concat("<",str(?prop),'> "',str(?val),'"'),
                                 concat("<",str(?prop),"> <",str(?val),">")
                                 ) as ?lexfeat)
                         } GROUP BY ?entry ?lexinfo
                         }
                     }
            }
        """

        generated=0
        processed_entries=[]
        qres = lex.query(query)
        for row in qres:
            if row.baseform!=None:
                entry="<"+str(row.entry)+">"
                baseform=str(row.baseform)
                itype=str(row.itype)
                try:
                    output=self.generate(baseform, itype, lexinfo=row.lexinfo, skip_incomplete_forms=skip_incomplete_forms,strict_mode=strict_mode)
                    # print(output)
                    if len(output)>0:
                        if compact==True:
                            output={ form : [ parse_lfeats("; ".join(tags), str) ] for form,tags in output.items() }
                        if output_file==None:
                            print(baseform+" "+re.sub(r"<[^>\#]*[\#/]([^\#/>]*)>",r"lexinfo:\1",str(row.lexinfo)))
                            for form, tags in output.items():
                                if not form.startswith("*") or form[1:] != baseform: # return hypotheses only if different from baseform
                                    for tag in tags:
                                        if isinstance(tag,str):
                                            tag=re.sub(r"<[^>\#]*[\#/]([^\#/>]*)>",r"lexinfo:\1",tag)   # simplified
                                        else:
                                            print("warning: expected string but got "+str(tag))      # for debugging
                                        print(form+" "+str(tag))
                                        form=" "*len(form)
                            print()
                        else:
                            for form, tags in output.items():
                                if not form.startswith("*") or form[1:] != baseform: # return hypotheses only if different from baseform
                                    if form.startswith("*"):
                                        form=form[1:]
                                    for tag in tags:
                                        generated+=1
                                        myuri="<"+str(row.entry)+"_hypo_"+str(generated)+">"
                                        output_file.write(entry+" ontolex:lexicalForm "+myuri+".\n")
                                        output_file.write(myuri+" a ontolex:Form, morph:HypotheticalForm;\n")
                                        if len(tag)>0 and isinstance(tag,str):
                                            output_file.write("  "+tag+";\n")
                                        output_file.write("  morph:inflectionType "+"<"+itype+">;")
                                        output_file.write("  ontolex:writtenRep \""+form+"\" .\n\n")
                                        output_file.flush()

                except:
                    traceback.print_exc()
            if not entry in processed_entries:
                processed_entries.append(entry)
            if output_file!=None:
                sys.stderr.write(str(generated)+" forms generated for "+str(len(processed_entries))+" entries\r")
                sys.stderr.flush()
        if output_file!=None:
            output_file.close()
            sys.stderr.write("\n")
            sys.stderr.flush()

if __name__ == "__main__":

    args=argparse.ArgumentParser(description="given OntoLex-Morph inflection rules and an OntoLex dictionary, generate all forms; rule extraction is written in SPARQL. Note that internally, we use sed, so make sure this is installed on your system ;)")
    args.add_argument("lex", type=str, help="OntoLex dictionary")
    args.add_argument("-anno", "--annotation_model", type=str, help="OLiA annotation model that defines possible pairs of lexinfo features and tags, defaults to the value of lex")
    args.add_argument("-flex","--inflection_types", type=str, nargs="?", help="OntoLex inflection rules, defaults to the value of lex; however, it's much faster if it is clearly separated ;)",default=None)
    args.add_argument("-rules", "--rule_extractor", type=str, nargs="?", help="SPARQL script to retrieve rules from the flex argument, defaults to rule2sed.sparql in the local directory; note: we expect it to return the following variable names ?itype ?transformation", default=None)
    args.add_argument("-no_stars", "--skip_incomplete_forms", action="store_true", help="by default, we return all generation hypotheses, including those that are marked for postprocessing with morphophonological rules. With this flag, we only return completed forms")
    args.add_argument("-loose", "--disable_strict_mode", action="store_true", help="in strict (default) mode, we generate on the basis of the lexinfo:partOfSpeech of a lexical entry, in loose mode, we try *all possible parts of speech* if no POS is provided")
    args.add_argument("-compact", "--compact_features", action="store_true",help="if set, lump all features of a given form together, by default, each combination of features constitutes a new form")
    args.add_argument("-o","--ontolex", type=str, nargs="?", help="instead of human-readable output to stdout, write OntoLex data into output file",default=None)
    args=args.parse_args()

    if args.inflection_types==None:
        args.inflection_types=args.lex
    if args.annotation_model==None:
        args.annotation_model=args.lex
    if args.rule_extractor==None:
        args.rule_extractor="rule2sed.sparql"

    sys.stderr.write("build generator (this may take a while)\n")
    sys.stderr.flush()
    generator=Generator(args.inflection_types, args.rule_extractor, args.annotation_model, skip_incomplete_forms=args.skip_incomplete_forms,strict_mode=not args.disable_strict_mode)
    sys.stderr.write("start generation\n")
    sys.stderr.flush()
    generator.generate_for_dict(args.lex,output_file=args.ontolex,compact=args.compact_features)
    sys.stderr.write("generation completed\n")
    sys.stderr.flush()
