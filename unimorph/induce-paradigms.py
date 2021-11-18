import sys,io,re,traceback,argparse,random

#
# this is a side.experiment on the induction of paradigms from raw UniMorph files
# it uses the same morph(eme) induction strategies as the RDF converter
# i.e., it systematically lacks any support for umlaut and ablaut (which are frequent
# phenomena in German), as well as for verbal inflection (which is generated from the
# base, not the infinitive, and this distracts the morph induction)
#
# we provide the most frequent inflection per combination of stem ending and part of speech
# this operates on raw UniMorph data
#
# the rationale of this experiment was to motivate a possible extension of the paradigm
# metadata to include substring matches
# at the moment, we would not include that in OntoLex-Morph
# instead, the "naive" strategy for *generation* would take the most frequent paradigm
# per part of speech
#
# for the German data, this is equivalent to
# $> python3 induce-paradigms.py src/deu/deu --eval -p 2
# which yields
# a: 0.3912813178664124
# p: 0.5889810237601658
# r: 0.5382541533080735
# f: 0.56247620497982184

# if unlimited string matches are included, we can boost the test error that to
# a: 0.5354006891185951
# p: 0.9243907119554788
# r: 0.5599209578054167
# f: 0.6974084262342551
# $> python3 induce-paradigms.py src/deu/deu --eval

# cf. train error
# a: 0.5814665484416041
# p: 0.9951895544611156
# r: 0.5831054441741464
# f: 0.73535105628960436
# $> python3 induce-paradigms.py src/deu/deu

# recall is pretty stable, this is mostly gaps in umlaut and verbal inflection

args=argparse.ArgumentParser(description="read UniMorph file, extrapolate candidate paradigms")
args.add_argument("file", type=str, help="UniMorph data file")
args.add_argument("-p","--plimit", type=int, help="use only the top p (most frequent) automatically bootstrapped paradigms, defaults to -1 (unlimited)", default=-1)
args.add_argument("-eval","--eval", action="store_true", help="if set, single out a 10% random test set (sampled over lemmas) and provide test error instead of training error")
args.add_argument("-i","--iterations", type=int, help="number of iterations for evaluation, entails --eval")
args=args.parse_args()

if args.iterations!=None:
    args.eval=True
if args.iterations==None:
    args.iterations=1

# limit to top plimit paradigms
plimit=args.plimit

last_lemma=None
test=True
train=True  # by default, we evaluate on the trainset

while(args.iterations>0):
    args.iterations-=1
    with open(args.file,"r") as input:
        entry2feats2morph={}
        entry2feats2form={}
        for line in input:
            line=line.strip()
            fields=line.split("\t")
            if len(fields)>2:
                lemma=fields[0]
                if(last_lemma!=lemma):
                    last_lemma=lemma
                    if args.eval:
                        test=random.random()<=0.1 # 10%
                        train=not test

                form=fields[1]
                feats=fields[2]
                pos=feats[0]
                feats=";".join(sorted(set(feats.split(";"))))
                FORM=form.lower()
                LEMMA=lemma.lower()
                entry=LEMMA+"_"+pos

                if test:
                    if not entry in entry2feats2form:
                        entry2feats2form[entry] = { feats: form }
                    elif not feats in entry2feats2form[entry]:
                        entry2feats2form[entry][feats] = form
                    elif form.lower() != entry2feats2form[entry][feats].lower():
                        sys.stderr.write("warning: could not overwrite \""+\
                            entry2feats2form[entry][feats]+"\" with \""+form+"\" for "+entry+"/"+feats+"\n")
                        sys.stderr.flush()

                if train:
                    morph=None
                    if(FORM==LEMMA):
                        morph="0"
                    elif FORM.startswith(LEMMA):
                        morph="-"+FORM[len(LEMMA):]
                    elif FORM.endswith(LEMMA):
                        morph=FORM[0:-len(LEMMA)]+"-"
                    elif LEMMA in FORM:
                        morph=FORM[0:FORM.index(LEMMA)]+"-...-"+FORM[FORM.index(LEMMA)+len(LEMMA):]
                    if morph!=None:
                        if not entry in entry2feats2morph:
                            entry2feats2morph[entry]={feats : morph }
                        elif not feats in entry2feats2morph[entry]:
                            entry2feats2morph[entry][feats]=morph
                        elif morph != entry2feats2morph[entry][feats]:
                            sys.stderr.write("warning: could not overwrite \""+\
                                entry2feats2morph[entry][feats]+"\" with \""+morph+"\" for "+entry+"/"+feats+"\n")
                            sys.stderr.flush()

        class RLTree:
            """ right-to-left tree """

            def __init__(self):
                self.vals=[]
                self.subtrees={}

            def get(self, key=None):
                subtrees=self.subtrees
                if key==None or len(key)==0:
                    vals=list(self.vals)
                    for k,t in subtrees.items():
                        for v in t.get():
                            if not v in vals:
                                vals.append(v)
                    return vals
                elif key[-1] in subtrees:
                    return subtrees[key[-1]].get(key[0:-1])
                return None

            def add(self,key:str, val:str):
                subtrees=self.subtrees
                if key==None or len(key)==0:
                    if not val in self.vals:
                        self.vals.append(val)
                else:
                    if not key[-1] in subtrees:
                        subtrees[key[-1]]=RLTree()
                    subtrees[key[-1]].add(key[0:-1],val)
                self.subtrees=subtrees

            def get_subkeys(self, key=None):
                """ return sub-keys (non-transitive) """
                subtrees=self.subtrees
                if key==None or len(key)==0:
                    return list(subtrees.keys())
                else:
                    if key[-1] in subtrees:
                        keys=subtrees[key[-1]].get_subkeys(key=key[0:-1])
                        return [ k+key[-1] for k in keys ]
                    else:
                        return []

        def feat2morph(keys, key2feat2morph: dict, type=dict):
            """ return majority paradigm for a collection of keys """
            if isinstance(keys,str):
                keys=[keys]
            feat2morph2freq={}
            for key in keys:
                if key in key2feat2morph:
                    for feat,morph in key2feat2morph[key].items():
                        if not feat in feat2morph2freq:
                            feat2morph2freq[feat] = { morph : 1 }
                        elif not morph in feat2morph2freq[feat]:
                            feat2morph2freq[feat][morph] = 1
                        else:
                            feat2morph2freq[feat][morph]+=1
            feat2morph={}
            for feat in sorted(feat2morph2freq.keys()):
                cand=None
                cf=0
                for morph, freq in feat2morph2freq[feat].items():
                    if freq>cf:
                        cand=morph
                        cf=freq
                if cand !=None:
                    feat2morph[feat]=cand
            return type(feat2morph)

        tree=RLTree()
        for entry in entry2feats2morph:
            tree.add(entry,entry)

        # keys=[ "", "N", "Na", "_N"]
        #
        # for key in keys:
        #     print(key)
        #     print(tree.get(key))
        #     print(tree.get_subkeys(key))
        #     print()

        # we construct paradigms in a top-down fashion:
        # we start with the last character, make the most frequent rules the default paradigm
        # and then extend the keys to the left and add alternative paradigms whenever encountered

        candidates=tree.get_subkeys("")
        paradigms={}
        cand2feats={}
        while(len(candidates)>0):
            cand=candidates[0]
            entries=tree.get(cand)
            cand2feats[cand]=feat2morph(entries,entry2feats2morph,str)
            parent=""
            if len(cand)>1:
                parent=cand[1:]
            if not parent in cand2feats or cand2feats[parent] != cand2feats[cand]:
                 paradigms[cand]=len(entries)
            candidates=candidates[1:]
            candidates+=tree.get_subkeys(cand)

        paradigms=[ (freq,p) for p,freq in paradigms.items() ]
        paradigms=list(reversed(sorted(paradigms)))
        #total=len(tree.get(""))
        #print(total,type(total),len(paradigms))

        # print(len(paradigms))

        if plimit>=0:
            paradigms=paradigms[0:plimit]


        # for f,p in paradigms[0:50]:
        #     #print(f"{f/total:.3f}",f,p)
        #     print(f,p)

        # print(paradigms)

        paradigms = { p: feat2morph(tree.get(p),entry2feats2morph,dict) for _,p in paradigms }

        # print(paradigms)

        tp=0
        fp=0
        fn=0
        total=0

        for entry in entry2feats2form:
            base=re.sub(r"_.*","",entry)
            paradigm=None
            cand=entry
            while len(cand)>0:
                # print(cand)
                if cand in paradigms:
                    paradigm=paradigms[cand]
                    # print(cand,paradigm)
                    break
                # print(cand)
                cand=cand[1:]
            feats2predicted={}
            feats2form={ feats : None for feats in entry2feats2form[entry].keys() }
            for feat in entry2feats2form[entry]:
                total+=1
                if paradigm!=None and feat in paradigm:
                    morph=paradigm[feat]
                    pfx=""
                    sfx=""
                    if "-...-" in morph:
                        pfx=morph[0:morph.index("-...-")]
                        sfx=morph[morph.index("-...-")+len("-...-"):]
                    elif morph.endswith("-"):
                        pfx=morph[0:-1]
                    elif morph.startswith("-"):
                        sfx=morph[1:]
                    elif morph!="0":
                        sys.stderr.write("unsupported morph schema \""+morph+"\", skipped\n")
                        sys.stderr.flush()
                    feats2form[feat]=pfx+base+sfx
                    # print(entry,base,feats2form[feat])
                if feats2form[feat]==None:
                    fn+=1
                elif feats2form[feat].lower()==entry2feats2form[entry][feat].lower():
                    tp+=1
                else:
                    fp+=1
            a=tp/total
            p=0
            if tp+fp!=0:
                p=tp/(tp+fp)
            r=0
            if tp+fp!=0:
                r=tp/(tp+fn)
            f=0
            if r+p!=0:
                f=2*p*r/(r+p)
            results=[total,tp,fp,fn,a,p,r,f]
            results=[str(r) for r in results ]
            sys.stderr.write("\t".join(results)+"\r")
            sys.stderr.flush()
        sys.stderr.write(" "*120+"\r"+"\t".join(results)+"\n")
