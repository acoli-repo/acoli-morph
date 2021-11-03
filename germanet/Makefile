all: deu

deu:	tarql src
	mkdir deu
	./tarql --dedup 5000 -t --base http://purl.org/acoli/morph/de/GermaNet16.0 --write-base tsv2ontolex.sparql src/split_compounds_from_GermaNet16.0.txt | gzip -f > deu/deu.ttl.gz

src:
	mkdir src
	wget https://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet16.0.txt -O src/split_compounds_from_GermaNet16.0.txt
	sed -i s/'^[^a-zA-Z0-9]*$'// src/split_compounds_from_GermaNet16.0.txt

bin:
		mkdir bin

bin/tarql: bin
		@(cd bin; \
		  wget -nc https://github.com/tarql/tarql/releases/download/v1.2/tarql-1.2.tar.gz;\
		  tar -xvf tarql-1.2.tar.gz; \
		  ln -s tarql-*/ tarql;)

tarql: bin/tarql
		@if [ ! -e tarql ]; then ln -s bin/tarql/bin/tarql tarql ; fi
