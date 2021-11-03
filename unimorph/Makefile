all: deu

src/deu:
	mkdir -p src/deu
	git clone https://github.com/unimorph/deu src/deu

bin:
	        mkdir bin

bin/tarql: bin
	        @(cd bin; \
	          wget -nc https://github.com/tarql/tarql/releases/download/v1.2/tarql-1.2.tar.gz;\
	          tar -xvf tarql-1.2.tar.gz; \
	          ln -s tarql-*/ tarql;)

tarql: bin/tarql
	        @if [ ! -e tarql ]; then ln -s bin/tarql/bin/tarql tarql ; fi

deu: src/deu tarql
		 @echo build German sample data
	   mkdir deu
		 ./tarql --dedup 5000 -t --base http://purl.org/acoli/morph/UniMorph/deu/ --write-base -H tsv2ontolex.sparql src/deu/deu | gzip -f > deu/deu.ttl.gz
