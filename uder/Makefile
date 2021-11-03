all: src de/DErivBase/0.5

bin:
	mkdir bin

bin/tarql: bin
	@(cd bin; \
	  wget -nc https://github.com/tarql/tarql/releases/download/v1.2/tarql-1.2.tar.gz;\
	  tar -xvf tarql-1.2.tar.gz; \
	  ln -s tarql-*/ tarql;)

tarql: bin/tarql
	@if [ ! -e tarql ]; then ln -s bin/tarql/bin/tarql tarql ; fi

src:
	@echo retrieve source data
	git clone https://github.com/lukyjanek/universal-derivations src

src/py3env: src
	python3 -m venv src/py3env

de/DErivBase/0.5: src/py3env tarql
	@echo build German sample data
	@# note that we cannot build everything at once, because some components require to download external resources beforehand
	@(cd src/de/DErivBase; make)
	@echo build German OntoLex
	mkdir -p de/DErivBase/0.5
	./tarql -t --base http://purl.org/acoli/morph/UDer/de/DErivBase/0.5/ --write-base -H sparql/relations.sparql src/de/DErivBase/0.5/relations.tsv | tee de/DErivBase/0.5/relations.ttl
	./tarql -t --base http://purl.org/acoli/morph/UDer/de/DErivBase/0.5/ --write-base -H sparql/relations.sparql src/de/DErivBase/0.5/singletons.tsv | tee de/DErivBase/0.5/singletons.ttl
