all: src deu

deu: src
	mkdir deu
	cat src/lexicon | \
	sed -e s/'\t'/' '/g \
			-e s/"<>"/"\&lt;\&gt;"/g \
			-e s/'>'/'>\t'/g \
			-e s/'<'/'\t<'/g \
			-e s/'\t\t*'/'\t'/g \
			-e s/'\&lt;'/'<'/g \
			-e s/'\&gt;'/'>'/g \
			> deu/lexicon.tsv
	python3 fst2ontolex.py src/flexion.fst > deu/flexion.ttl

src:
	wget -nc https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/morphisto/source-archive.zip
	mkdir tmp
	unzip -d tmp source-archive.zip "morphisto/trunk/src/*"
	mv tmp/morphisto/trunk/src src
	@(for file in `find src | egrep '/.svn$$'`; do rm -rf $$file; done)
	rm -rf tmp
	@(cd src; make)
