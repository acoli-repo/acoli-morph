all: src deu

deu: src
	mkdir deu
	python3 fst2ontolex.py \
		-base "http://purl.org/acoli/morph/morphisto/de/flex/" \
		src/flexion.fst > deu/flexion.ttl
	python3 lex2ontolex.py \
		-base "http://purl.org/acoli/morph/morphisto/de/lex/" \
		-rules "http://purl.org/acoli/morph/morphisto/de/flex/" \
		-anno "http://purl.org/acoli/morph/morphisto/de/annomodel#" \
		src/lexicon | \
		rapper -i turtle - "http://purl.org/acoli/morph/morphisto/de/lex/" -o turtle > deu/lexicon.ttl
	python3 generate.py deu/lexicon.ttl -anno annomodel.ttl -flex deu/flexion.ttl -rules rule2sed.sparql -compact > deu/output-compact.txt &
	# python3 generate.py deu/lexicon.ttl -anno annomodel.ttl -flex deu/flexion.ttl -rules rule2sed.sparql > deu/output-full.txt &
	# nice python3 generate.py deu/lexicon.ttl -anno annomodel.ttl -flex deu/flexion.ttl -rules rule2sed.sparql -o deu/output-full.ttl &
	nice python3 generate.py deu/lexicon.ttl -anno annomodel.ttl -flex deu/flexion.ttl -rules rule2sed.sparql -o deu/output-compact.ttl -compact
	gzip deu/output-compact.t*

src:
	wget -nc https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/morphisto/source-archive.zip
	mkdir tmp
	unzip -d tmp source-archive.zip "morphisto/trunk/src/*"
	mv tmp/morphisto/trunk/src src
	@(for file in `find src | egrep '/.svn$$'`; do rm -rf $$file; done)
	rm -rf tmp
	@(cd src; make)

test: all
	@# demonstrate how the generated rules work, human-readable output
	python3 generate.py deu/lexicon.ttl -anno annomodel.ttl -flex deu/flexion.ttl -rules rule2sed.sparql

clear:
	@if [ -e deu ]; then rm -rf deu; fi;

# eval_smor:
# 	@if [ ! -e UD_German-HDT.txt ]; then \
# 	  if [ ! -e UD_German-HDT ]; then git clone https://github.com/UniversalDependencies/UD_German-HDT; fi; \
# 		cat UD_German-HDT/*conllu | \
# 			egrep '^[0-9]' | \
# 			sed s/'^1\s'/'\n&'/ | \
# 			cut -f 2 | \
# 			perl -pe 's/([^\n])\n/\1 /g;' > UD_German-HDT.txt;\
# 		fi;
#
#
# sfst: src
# 	git clone https://github.com/santhoshtr/sfst
# 	cp src/*fst sfst/data/SMOR
# 	cd sfst/data/SMOR; make smor.a
