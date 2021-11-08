all: links

init:
	@echo make sure the individual datasets are there
	@(for dir in ../*/; do if [ -e $$dir/Makefile ]; then if [ `cd $$dir; pwd` != `pwd` ]; then cd $$dir; make ; echo; cd -; fi; fi; done )

links: init
	@echo expand and link sample data for German
	if [ ! -e links ]; then mkdir links; fi
	@datasets="../germanet/ ../unimorph/ ../uder/ ../morphisto/";\
	for source in $$datasets; do \
		for target in `echo $$datasets | sed s/' '/'\n'/g | egrep -A 1000 -m 1 $$source | grep -v $$source`; do \
				for lang in "de"; do \
					tdir=links/$$lang; \
					if [ ! -e $$tdir ]; then mkdir -p $$tdir; fi; \
					\
					tgt=$$tdir/`basename $$source`-`basename $$target`.ttl.gz; \
					if [ -e $$tgt ]; then \
						echo found $$tgt, skipping; \
					else \
						s=$$tdir/`basename $$source`.tmp; \
						t=$$tdir/`basename $$target`.tmp; \
						\
						echo $$tgt: linking $$source and $$target 1>&2; \
						(if [ -e $$s ]; then \
							echo reading from $$s 1>&2; \
		 					cat $$s; \
						else \
							for sdata in `find $$source/$$lang* | egrep "ttl.gz$$|ttl$$"`; do \
								echo extract source vocabulary 1>&2; \
								if echo $$sdata | egrep 'gz$$' >/dev/null; then \
									echo reading from $$sdata 1>&2; \
									gunzip -c $$sdata; \
									echo $$sdata gunzipped 1>&2; \
								else \
									echo reading from $$sdata 1>&2; \
									cat $$sdata; \
									echo $$sdata read  1>&2; \
								fi | \
								rapper -e -i turtle - "#" | \
								egrep "writtenRep|(lexical|canonical|base)Form";\
							done | tee $$s; \
						fi ; \
						\
						if [ -e $$t ]; then \
							echo reading from $$t 1>&2; \
							cat $$t; \
						else \
							for tdata in `find $$target/$$lang* | egrep "ttl.gz|ttl$$"`; do \
									echo extract target vocabulary 1>&2; \
									if echo $$tdata | egrep 'gz$$' >/dev/null; then \
										echo reading from $$tdata 1>&2; \
										gunzip -c $$tdata; \
										echo $$tdata gunzipped 1>&2; \
									else \
										echo reading from $$tdata 1>&2; \
										cat $$tdata; \
										echo $$tdata read 1>&2; \
									fi | \
									rapper -e -i turtle - "#" | \
									egrep "writtenRep|(lexical|canonical|base)Form";\
							done | tee $$t; \
						fi ) \
						> $$tgt.tmp.ttl ; # mkfifo: & \
						echo reduced dataset to `cat $$tgt.tmp.ttl | wc -l` triples 1>&2;\
						\
						echo infer linking 1>&2; \
						arq --data $$tgt.tmp.ttl --query=link.sparql | tee /dev/stderr | gzip -f > $$tgt;\
					fi;\
				done;\
			done;\
		done;\
		#rm links/*/*tmp
