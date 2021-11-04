all: src

src:
	wget -nc https://storage.googleapis.com/google-code-archive-source/v2/code.google.com/morphisto/source-archive.zip
	mkdir tmp
	unzip -d tmp source-archive.zip "morphisto/trunk/src/*"
	mv tmp/morphisto/trunk/src src
	@(for file in `find src | egrep '/.svn$$'`; do rm -rf $$file; done)
	rm -rf tmp
