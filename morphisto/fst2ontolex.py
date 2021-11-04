import re,sys,os,traceback,argparse
from pprint import pprint
import urllib.parse

args=argparse.ArgumentParser(description="given an (S)FST transducer for inflections, create an OntoLex-Morph representation")
args.add_argument("fst",type=str, help="fst inflection file")
args.add_argument("-base", "--base_uri", nargs="?", type=str, help="base uri, defaults to #", default="#")
args=args.parse_args()

# - a new rule begins in a new line
# - FST rules have the following basic structure:
#   RULE := "$"PRE_STATE"$" "=" SOURCE ":" TARGET  ( TAB "$"POST_STATE"$")? ([ "|\" ...]*
#   TARGET := "{" ("<"TAG*">"|STRING)+ "}" | "<"TAG">"
#   SOURCE := "{" ("<"TAG*">"|STRING)+ "}" | "<"TAG">"
# - FST rules terminate if no POST_STATE is defined
# - Tags are enclosed by <>, strings are not enclosed, the surface string can be generated by dropping <[^>]*>

# the escaping rules aren't fully implemented
# for the conversion we point from the form to the inflection type, this is the
# nonterminal state (symbol) from which the sequence of inflection types is called

def my(identifier, prefix=""):
    """ uri escaping and prefix assigment """
    return prefix+":"+urllib.parse.quote(identifier)

state2in2out2next={}
with open(args.fst,"r") as input:
    lhs=None
    for line in input:
        if "%" in line:
            line=line[0:line.index("%")]
        line=line.strip()
        if line!="":
            print("LINE",line)
            if lhs==None:
                if "=" in line:
                    lhs=line.split("=")[0].strip()
                    line="=".join(line.split("=")[1:]).strip()
            if lhs!=None:
                rhs=line.strip()
                while(rhs.endswith("\\")):
                    line=input.readline()
                    if "%" in line:
                        line=line[0:line.index("%")]
                    line=line.strip()
                    rhs=rhs[0:-1]+" "+line

                print("RULE", lhs,"=>",rhs)

                for rule in rhs.split("|"):
                    rule=re.sub(r"\s+"," ",rule).strip()
                    if rule!="":
                        src=None
                        tgt=None
                        post=None
                        if "$" in rule.split(" ")[-1]:
                            post=rule.split(" ")[-1]
                            rule=" ".join(rule.split(" ")[0:-1]).strip()
                            src=""
                            tgt=""
                        if ":" in rule:
                            src=rule[0:rule.index(":")].strip()
                            tgt=rule[rule.index(":")+1:].strip()

                        if tgt!=None and ":" in tgt:
                            sys.stderr.write("warning: did not implement filters, yet, skipping rhs \""+rhs+"\"\n")
                            sys.stderr.flush()
                        elif None in [src,tgt]:
                            sys.stderr.write("warning: check rhs \""+rhs+"\" with sub-expression \""+rule+"\"\n")
                            sys.stderr.flush()
                        else:
                            try:
                                src=re.sub(r"[{}]","",src).strip()
                                tgt=re.sub(r"[{}]","",tgt).strip()

                                if not lhs in state2in2out2next:
                                    state2in2out2next[lhs] = { src : { tgt : [] }}
                                elif not src in state2in2out2next[lhs]:
                                    state2in2out2next[lhs][src] = { tgt : [] }
                                else:
                                    state2in2out2next[lhs][src][tgt] = []

                                if post!=None and not post in state2in2out2next[lhs][src][tgt]:
                                    state2in2out2next[lhs][src][tgt].append(post)
                            except:
                                traceback.print_exc()
                lhs=None

# pprint(state2in2out2next)

print("@prefix : <"+args.base_uri+"> .")
print("""
@prefix ontolex: <http://www.w3.org/ns/lemon/ontolex#> .
@prefix synsem: <http://www.w3.org/ns/lemon/synsem#> .
@prefix decomp: <http://www.w3.org/ns/lemon/decomp#> .
@prefix vartrans: <http://www.w3.org/ns/lemon/vartrans#> .
@prefix lime: <http://www.w3.org/ns/lemon/lime#> .
@prefix morph: <http://www.w3.org/ns/lemon/morph#> .

@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>.
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>.
@prefix owl: <http://www.w3.org/2002/07/owl#>.
@prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
@prefix skos: <http://www.w3.org/2004/02/skos#>.
@prefix dbr: <http://dbpedia.org/resource/>.
@prefix dbo: <http://dbpedia.org/ontology/>.
@prefix void: <http://rdfs.org/ns/void#>.
@prefix lexinfo: <http://www.lexinfo.net/ontology/2.0/lexinfo#>.
@prefix semiotics: <http://www.ontologydesignpatterns.org/cp/owl/semiotics.owl#>.
@prefix oils: <http://lemon-model.net/oils#>.
@prefix dct: <http://purl.org/dc/terms/>.
@prefix provo: <http://www.w3.org/ns/prov#>.
""")

for state in state2in2out2next:
    itype=my("type#"+state)
    print(itype+" a ontolex:InflectionType ; rdfs:label \""+state+"\".")
    for source in state2in2out2next[state]:
        for target in state2in2out2next[state][source]:
            for post in state2in2out2next[state][source][target]:
                print(itype+" morph:next "+my("type#"+post)+".")
            rule=my("rule#"+state+"_"+source+">"+target)
            print(itype+" morph:inflectionRule "+rule+".")
            print(rule+" a morph:InflectionRule; morph:example \"..."+source+" > ..."+target+"\"", end="; ")
            s=source
            t=target
            if s=="<>":
                s=""
            if t=="<>":
                t=""
            for symbol in ["/", "$", "^", "&"]:
                s=("\\"+symbol).join(s.split(symbol))
                t=("\\"+symbol).join(t.split(symbol))

            replacement="s/"+s+"$/"+t+"/"       # with s+"$", we assume left-to-right replacement: TODO: TBC
            print("morph:replacement \""+replacement+"\".")
