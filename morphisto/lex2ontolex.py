import re,sys,os,traceback,argparse
from pprint import pprint
import urllib.parse

args=argparse.ArgumentParser(description="given an (S)FST lexicon, create an OntoLex-Morph representation. Note that it only supports the entry types of Morphisto/SMOR.")
args.add_argument("lex",type=str, help="lexicon.lex")
args.add_argument("-base", "--base_uri", nargs="?", type=str, help="base uri, defaults to #", default="#")
args.add_argument("-i", "--interactive", action="store_true", help="if set, do not convert, but run an interface for interactive exploration of the lexicon")
args=args.parse_args()

# this defines the Morphisto schema
# the type is defined in the first column
# if the last field is "SUB_TYPE", then its value is a key in type2fields and the following fields correspond to those of this key
type2fields={
    "<Deriv_Stems>" : [ "ENTRY_TYPE", "FORM", "POS", "RULE_TYPE", "META" ],
        # words with irregular stem alternations
    "<Pref_Stems>" : [ "ENTRY_TYPE", "FORM", "MORPH_TYPE", "BASE_POS*", "META" ],
        # * indicates that there may be multiple values
    "<Base_Stems>" : [ "ENTRY_TYPE", "FORM", "POS", "RULE_TYPE", "META", "PARADIGM" ],
    "<Suff_Stems>" : [ "ENTRY_TYPE", "RULES", "META", "RULE_TYPE", "BASE_POS", "FORM", "RESULT_POS", "MORPH_TYPE", "BASE_TYPE", "RESULT_META", "RESULT_PARADIGM"],
    "<Kompos_Stems>" : [ "ENTRY_TYPE", "FORM", "POS", "RULE_TYPE", "META"],
    "<Initial>" : [ "ENTRY_TYPE" , "SUB_TYPE"],
    "<ge>" : [ "ENTRY_TYPE", "SUB_TYPE"],
    "<NoDef>" : [ "ENTRY_TYPE", "SUB_TYPE"],
    "<QUANT>" : [ "ENTRY_TYPE", "SUB_TYPE"],
    "<NoHy>" : [ "ENTRY_TYPE", "SUB_TYPE"] }

entries=[]
# array of dicts

with open(args.lex,"r") as input:
    for line in input:
        line=line.strip()
        if len(line)>0:
            line=" ".join(line.split("\t"))
            line="&lt;&gt;".join(line.split("<>"))
            line=">\t".join(line.split(">"))
            line="\t<".join(line.split("<"))
            line="\t".join(line.split("\t\t"))
            line="<>".join(line.split("&lt;&gt;"))
            line=line.strip()
            fields=line.split("\t")
            entry={}
            while len(fields)>0 and fields[0] in type2fields and "SUB_TYPE" in type2fields[fields[0]]:
                for field,val in zip(type2fields[fields[0]],fields):
                    if field=="SUB_TYPE":
                        break
                    elif not field in entry:
                        entry[field] = [val]
                    elif not val in entry[field]:
                        entry[field].append(val)
                    fields=fields[1:]
            if len(fields)>0:
                type=fields[0]
                if not type in type2fields:
                    raise Exception("unsupported field type \""+type+"\", please use one of "+", ".join(type2fields.keys()))
                keys=type2fields[type]
                while(len(keys)>0 and len(fields)>0):
                    field=keys[0]
                    val=fields[0]
                    if(field.endswith("*") and len(keys)>len(fields)):
                        fields=fields[1:]
                    else:
                        fields=fields[1:]
                        keys=keys[1:]
                    if field.endswith("*"):
                        field=field[0:-1]
                    if not field in entry:
                        entry[field] = [val]
                    elif not val in entry[field]:
                        entry[field].append(val)
            # pprint(entry)
            entries.append(entry)

# we now compile all forms out
for nr in range(len(entries)):
    entry=entries[nr]
    if "FORM" in entry:
        forms=[]
        for string in entry["FORM"]:
            for form in string.split("/"):
                if not ":" in form:
                    if not form in forms:
                        forms.append(form)
                if ":" in form:
                    form=" ".join(form.split("<>")) # now, " " is the empty character
                    for form in [ re.sub(r":.","",form), re.sub(r".:","",form) ]:
                        form=form.strip()
                        if not form in forms:
                            forms.append(form)
        entry["FORM"]=forms
        entries[nr]=entry

# indexing: point to entries
key2val2entries={}
for id,entry in enumerate(entries):
    for key in entry.keys():
        for val in entry[key]:
            if not key in key2val2entries:
                key2val2entries[key]= { val : [id]}
            elif not val in key2val2entries[key]:
                key2val2entries[key][val] = [id]
            elif not id in key2val2entries[key][val]:
                key2val2entries[key][val].append(id)

# pprint(entries)

if args.interactive:
    sys.stderr.write("enter a search term of the form key (for all values of key) or key=val (for rows with key=val), both key and val can contain the wildcard \"*\"\n")
    sys.stderr.write("you can concatenate multiple key[=val] expressions with <TAB> (tabulator)\n")
    sys.stderr.write("close with <ENTER>\n")
    sys.stderr.write("> ")
    sys.stderr.flush()
    for line in sys.stdin:
        line=line.strip()
        if line=="":
            sys.stderr.write("bye!")
            sys.exit()
        key2val_vals_keys={}
        for line in line.split("\t"):
            line=line.strip()
            if len(line)>0:
                val=None
                key=line
                if "=" in line:
                    key=line.split("=")[0].strip()
                    val="=".join(line.split("=")[1:]).strip()
                keys=[key]
                if "*" in key:
                    keys=[]
                    key=re.compile("^"+re.sub("\*",".*",key)+"$")
                    for k in key2val2entries.keys():
                        if key.match(k):
                            keys.append(k)
                vals=[]
                if val!=None and "*" in val:
                    val=re.compile("^"+re.sub("\*",".*",val)+"$")

                key2val_vals_keys[key]=(val,vals,keys)

        rows=None
        for key,(val,vals,keys) in list(key2val_vals_keys.items()):
            for k in keys:
                if k in key2val2entries:
                    if val==None:
                        vals=sorted(set(vals+list(key2val2entries[k].keys())))
                    elif isinstance(val,str):
                            if val in key2val2entries[k]:
                                if rows==None:
                                    rows=key2val2entries[k][val]
                                else:
                                    rows=[ r for r in rows if r in key2val2entries[k][val] ]
                    else:
                        myrows=[]
                        for v in key2val2entries[k]:
                            if val.match(v):
                                if not v in vals:
                                    vals.append(v)
                                myrows+=key2val2entries[k][v]
                        if rows==None:
                            rows=myrows
                        else:
                            rows=[ r for r in rows if r in myrows ]
            key2val_vals_keys[key]=(val,vals,keys)

        if rows!=None:
            for e in rows:
                print("\t".join( [ ",".join(vals) for vals in entries[e].values()]))

        for key,(val,vals,keys) in key2val_vals_keys.items():
            if val==None or len(vals)>1:
                print("VALS: "+", ".join(sorted(set(vals))))
            #if len(keys)>1 or not isinstance(key,str):
            print("KEYS: "+", ".join(sorted(set(keys)))+"\n")
        sys.stderr.write("> ")
        sys.stderr.flush()