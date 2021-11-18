all: deu

src/deu:
	mkdir -p src/deu
	git clone https://github.com/unimorph/deu src/deu

olia:
	@echo create local mirror of relevant OLiA concepts
	wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/experimental/unimorph/unimorph.owl -P olia/
	wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/experimental/unimorph/unimorph-link.rdf -P olia/
	wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/core/olia.owl -P olia/
	wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/lexinfo-link.rdf -P olia/
	wget -nc https://raw.githubusercontent.com/acoli-repo/olia/master/owl/stable/lexinfo.owl -P olia/
	arq  --data olia/olia.owl \
			 --namedGraph olia/unimorph.owl \
			 --namedGraph olia/unimorph-link.rdf \
			 --namedGraph olia/lexinfo-link.rdf \
			 --namedGraph olia/lexinfo.owl \
			 --query unimorph2lexinfo.sparql > olia/lexinfo2unimorph.ttl

bin:
	        mkdir bin

bin/tarql: bin
	        @(cd bin; \
	          wget -nc https://github.com/tarql/tarql/releases/download/v1.2/tarql-1.2.tar.gz;\
	          tar -xvf tarql-1.2.tar.gz; \
	          ln -s tarql-*/ tarql;)

tarql: bin/tarql
	        @if [ ! -e tarql ]; then ln -s bin/tarql/bin/tarql tarql ; fi

deu: src/deu tarql olia
	   mkdir deu
		 @echo build German sample data
		 ./tarql --dedup 5000 -t --base http://purl.org/acoli/morph/UniMorph/deu/ --write-base -H tsv2ontolex.sparql src/deu/deu > deu/deu.ttl
		 @echo bootstrap lexinfo from UniMorph-OLiA linking
		 arq --data deu/deu.ttl \
		 		 --namedGraph olia/lexinfo2unimorph.ttl   \
				 --query olia-link.sparql >> deu/deu.ttl
		gzip deu/deu.ttl

generate: all
	@# not integrated with overall make yet, this is an experimental feature
	arq --data deu/deu.ttl.gz --query generate.sparql > deu/deu-generated.ttl 

clear:
	@for dir in olia deu; do if [ -e $$dir ]; then rm -rf $$dir; fi; done
