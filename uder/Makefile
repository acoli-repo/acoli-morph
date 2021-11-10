all: src de/DErivBase/0.5

bin:
	mkdir bin

bin/tarql: bin
	@(cd bin; \
	  wget -nc https://github.com/tarql/tarql/releases/download/v1.2/tarql-1.2.tar.gz;\
	  tar -xvf tarql-1.2.tar.gz; \
	  ln -s tarql-*/ tarql;)

olia:
		@echo create local mirror of relevant OLiA concepts
		wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/uder.owl -P olia/
		wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/uder-link.rdf -P olia/
		wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/core/olia.owl -P olia/
		wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/lexinfo-link.rdf -P olia/
		wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/lexinfo.owl -P olia/
		arq  --data olia/olia.owl \
					 --namedGraph olia/uder.owl \
					 --namedGraph olia/uder-link.rdf \
					 --namedGraph olia/lexinfo-link.rdf \
					 --namedGraph olia/lexinfo.owl \
					 --query sparql/uder2lexinfo.sparql > olia/lexinfo2uder.ttl

tarql: bin/tarql
	@if [ ! -e tarql ]; then ln -s bin/tarql/bin/tarql tarql ; fi

src:
	@echo retrieve source data
	git clone https://github.com/lukyjanek/universal-derivations src

src/py3env: src
	python3 -m venv src/py3env

de/DErivBase/0.5: src/py3env tarql olia
	@echo build German sample data
	@# note that we cannot build everything at once, because some components require to download external resources beforehand
	@(cd src/de/DErivBase; make)
	@echo build German OntoLex
	mkdir -p de/DErivBase/0.5
	./tarql --dedup 5000 -t --base http://purl.org/acoli/morph/UDer/de/DErivBase/0.5/ --write-base -H sparql/relations.sparql src/de/DErivBase/0.5/relations.tsv > de/DErivBase/0.5/relations.ttl
	./tarql --dedup 5000 -t --base http://purl.org/acoli/morph/UDer/de/DErivBase/0.5/ --write-base -H sparql/relations.sparql src/de/DErivBase/0.5/singletons.tsv > de/DErivBase/0.5/singletons.ttl

	@echo bootstrap lexinfo from UDer-OLiA linking
	for file in de/DErivBase/0.5/*.ttl; do \
		arq --data $$file \
				--namedGraph olia/lexinfo2uder.ttl   \
				--query sparql/olia-link.sparql >> $$file;\
	done;\
	gzip de/DErivBase/0.5/*.ttl
