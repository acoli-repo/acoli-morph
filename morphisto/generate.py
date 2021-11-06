import os,sys,re,rdflib,traceback,argparse,subprocess,tempfile
import hashlib
from pprint import pprint

class Generator:

    def __init__(self, inflection_types, rule_extractor, annotation_model, tmpdir=tempfile.TemporaryDirectory(), skip_incomplete_forms=True):
        """ inflection_types OntoLex-Morph file with InflectionType definitions
            rule_extractor SPARQL script to produce transformation scripts from inflection_types, must be a SELECT statement that returns the variables ?itype and ?transform,
            this implementation of the generator further assumes that it produces a sed script
            if you provide a tmpdir, we re-use existing sed files
            """
        self.skip_incomplete_forms=skip_incomplete_forms
        self.tmpdir=tmpdir

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

    def _parse_lfeats(self, lexinfo: str):
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

        return lprop2vals

    def generate(self, baseform, itype, lexinfo=None, concepts=None,skip_incomplete_forms=None):
        """ return dictionary of form -> features
            concept is a candidate concept from OLiA, empty => any
            lexinfo is a string of ;-separated lexinfo properties and values
            that describe the (lexical entry of the) base form
        """
        itype2rules=self.itype2rules
        concept2tags=self.concept2tags
        if skip_incomplete_forms==None:
            skip_incomplete_forms=self.skip_incomplete_forms

        if not itype in itype2rules:
            raise Exception("did not find paradigm (inflection type) \""+itype+"\"")

        if concepts==None or len(concepts)==0:
            concepts=concept2tags.keys()

        lexinfo=self._parse_lfeats(lexinfo)
        result={}
        input2feats={}
        for concept in concepts:
            for left, right, tag_feats in concept2tags[concept]:
                compatible=True
                tag_feats=self._parse_lfeats(tag_feats)
                for prop in lexinfo:
                    if prop in tag_feats:
                        vals=[ val for val in lexinfo[prop] if val in tag_feats[prop] ]
                        if len(vals)==0:
                            compatible=False
                            break;
                        else:
                            tag_feats[prop] = vals
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
        return result

    def _generate(self,sed_script,input):
        result=""
        error=""
        hash=hashlib.md5(sed_script.encode('utf-8')).hexdigest()

        tmpfile=os.path.join(self.tmpdir.name,hash+".sed")
        if not os.path.exists(tmpfile):
            with open(tmpfile,"wt") as output:
                output.write(sed_script)

        sed=["sed","-f",tmpfile]
        sed=subprocess.Popen(sed,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)

        result,error=sed.communicate((input.strip()+"\n").encode("utf-8"))
        if result!=None:
            result=result.decode("utf-8")
        if error!=None:
            error=error.decode("utf-8").strip()
        # print(result,error)
        if error!=None and len(error)>0:
            raise Exception(error+"\n"+\
                "input: \""+input+"\"\n"+\
                "sed script:\n"+("="*80)+"\n"+sed_script+"\n"+("="*80))
        return result.strip()

    def generate_for_dict(self, inputsource, skip_incomplete_forms=None):
        """ given an OntoLex resource with paradigm/inflection type annotations,
            generate all hyppthetical inflected forms
            at the moment, this is for debugging only, so we just print to stdout
        """

        if skip_incomplete_forms==None:
            skip_incomplete_forms=self.skip_incomplete_forms

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

        qres = lex.query(query)
        for row in qres:
            if row.baseform!=None:
                entry="<"+str(row.entry)+">"
                baseform=str(row.baseform)
                itype=str(row.itype)
                try:
                    for form, tags in self.generate(baseform, itype, lexinfo=row.lexinfo).items():
                        form=baseform+" > "+form
                        for tag in tags:
                            tag=re.sub(r"<[^>\#]*[\#/]([^\#/>]*)>",r"lexinfo:\1",tag)   # simplified
                            print(form+"\t"+tag)
                            form=" "*len(form)
                except:
                    traceback.print_exc()

if __name__ == "__main__":

    args=argparse.ArgumentParser(description="given OntoLex-Morph inflection rules and an OntoLex dictionary, generate all forms; rule extraction is written in SPARQL. Note that internally, we use sed, so make sure this is installed on your system ;)")
    args.add_argument("lex", type=str, help="OntoLex dictionary")
    args.add_argument("-anno", "--annotation_model", type=str, help="OLiA annotation model that defines possible pairs of lexinfo features and tags, defaults to the value of lex", default=None)
    args.add_argument("-flex","--inflection_types", type=str, nargs="?", help="OntoLex inflection rules, defaults to the value of lex; however, it's much faster if it is clearly separated ;)",default=None)
    args.add_argument("-rules", "--rule_extractor", type=str, nargs="?", help="SPARQL script to retrieve rules from the flex argument, defaults to rule2sed.sparql in the local directory; note: we expect it to return the following variable names ?itype ?transformation", default=None)
    args.add_argument("-no_stars", "--skip_incomplete_forms", action="store_true", help="by default, we return all generation hypotheses, including those that are marked for postprocessing with morphophonological rules. With this flag, we only return completed forms")
    args=args.parse_args()

    if args.inflection_types==None:
        args.inflection_types=args.lex
    if args.annotation_model==None:
        args.annotation_model=args.lex
    if args.rule_extractor==None:
        args.rule_extractor="rule2sed.sparql"

    generator=Generator(args.inflection_types, args.rule_extractor, args.annotation_model, skip_incomplete_forms=args.skip_incomplete_forms)
    generator.generate_for_dict(args.lex)