all: deu

deu:
	mkdir deu;
	for file in ../germanet/deu/deu.ttl.gz ../morphisto/deu/flexion.ttl ../morphisto/deu/lexicon.ttl ../uder/de/DErivBase/0.5/singletons.ttl.gz ../uder/de/DErivBase/0.5/relations.ttl.gz ../unimorph/deu/deu.ttl.gz ../linking/links/de/*ttl.gz; do \
		tgt=deu/`echo $$file | sed s/'^[^\/]*\/\([^\/]*\)\/.*'/'\1'/g;`.ttl;\
		echo $$tgt;\
		if echo $$file | egrep 'gz' >/dev/null; then \
			gunzip -c $$file;\
		else \
			cat $$file; \
		fi >>$$tgt; \
	done; \
	for file in deu/*ttl; do \
		rdf2hdt -i $$file `echo $$file | sed s/'\.ttl$$'//`.hdt; \
		rm $$file;\
	done;


clear:
	rm -rf deu *.hdt

refresh: clear all
