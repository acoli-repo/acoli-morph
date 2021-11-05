all: src deu

deu: src
	mkdir deu
	# cat src/lexicon | \
	# sed -e s/'\t'/' '/g \
	# 		-e s/"<>"/"\&lt;\&gt;"/g \
	# 		-e s/'>'/'>\t'/g \
	# 		-e s/'<'/'\t<'/g \
	# 		-e s/'\t\t*'/'\t'/g \
	# 		-e s/'\&lt;'/'<'/g \
	# 		-e s/'\&gt;'/'>'/g \
	# 		> deu/lexicon.tsv
	python3 fst2ontolex.py \
		-base "http://purl.org/acoli/morph/morphisto/de/flex/" \
		src/flexion.fst > deu/flexion.ttl
	python3 lex2ontolex.py \
		-base "http://purl.org/acoli/morph/morphisto/de/lex/" \
		-rules "http://purl.org/acoli/morph/morphisto/de/flex/" \
		-anno "http://purl.org/acoli/morph/morphisto/de/annomodel#" \
		src/lexicon | \
		rapper -i turtle - "http://purl.org/acoli/morph/morphisto/de/lex/" -o turtle > deu/lexicon.ttl

src:
	wget -nc https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/morphisto/source-archive.zip
	mkdir tmp
	unzip -d tmp source-archive.zip "morphisto/trunk/src/*"
	mv tmp/morphisto/trunk/src src
	@(for file in `find src | egrep '/.svn$$'`; do rm -rf $$file; done)
	rm -rf tmp
	@(cd src; make)
