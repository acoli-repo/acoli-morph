all: links

init:
	@echo make sure the individual datasets are there
	@(for dir in ../*/; do if [ -e $$dir/Makefile ]; then if [ `cd $$dir; pwd` != `pwd` ]; then cd $$dir; make ; echo; cd -; fi; fi; done )

links: init
	@echo expand and link sample data for German
	if [ ! -e links ]; then mkdir links; fi
	@datasets="../germanet/ ../unimorph/ ../uder/";\
	for source in $$datasets; do \
		for target in `echo $$datasets | sed s/' '/'\n'/g | egrep -A 1000 -m 1 $$source | grep -v $$source`; do \
				for lang in "de"; do \
					for sdata in `find $$source/$$lang* | egrep "ttl$$|ttl.gz$$"`; do \
							for tdata in `find $$target/$$lang* | egrep "ttl$$|ttl.gz$$"`; do \
								tdir=links/$$lang; \
								if [ ! -e $$tdir ]; then mkdir -p $$tdir; fi; \
								tgt=$$tdir/`basename $$source`-`basename $$target`.ttl.gz; \
								echo $$tgt: linking $$sdata and $$tdata 1>&2; \
								if [ -e $$tgt ]; then \
									echo found $$tgt, skipping; \
								else \
									s=$$tdir/`basename $$source`.tmp; \
									t=$$tdir/`basename $$target`.tmp; \
									\
									# mkfifo $$tgt.tmp.ttl; \
									( if [ -e $$s ]; then \
										 echo reading from $$s 1>&2; \
									 	 cat $$s; \
										else \
											echo extract source vocabulary 1>&2; \
											if echo $$sdata | egrep 'gz$$' >/dev/null; then \
												echo reading from $$sdata 1>&2; \
												gunzip -c $$sdata; \
												echo $$sdata gunzipped 1>&2; \
											else \
												echo reading from $$data 1>&2; \
												cat $$sdata; \
												echo $$sdata read  1>&2; \
											fi | \
											rapper -i turtle - "#" | \
											egrep "writtenRep|(lexical|canonical)Form" | tee $$s;\
											echo reading from $$s 1>&2; \
										fi;\
										\
										if [ -e $$t ]; then \
											echo reading from $$t 1>&2; \
											cat $$t;\
										else \
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
											rapper -i turtle - "#" | \
											egrep "writtenRep|(lexical|canonical)Form" | tee $$t;\
											echo reading from $$t 1>&2; \
										fi;\
									) > $$tgt.tmp.ttl ; # mkfifo: & \
									echo reduce dataset to `cat $$tgt.tmp.ttl | wc -l` triples 1>&2;\
									echo infer linking 1>&2; \
									arq --data wReps.ttl --query=link.sparql | tee /dev/stderr | gzip -f > $$tgt;\
									rm $$tgt.tmp.ttl;\
								fi;\
							done; \
						done;\
					done;\
				done;\
		done;\
		rm links/*/*tmp

# 		souces=`find $$dataset | egrep "\.ttl(\.gz)?$$"`;
#
# 		if [ -e $dataset/de ];
# 	@(if [ ! -e wReps.ttl ]; then \
# 		for file in ../germanet/deu/deu.ttl.gz ../unimorph/deu/deu.ttl.gz ../uder/de/DErivBase/0.5/*.ttl.gz; do \
# 			gunzip -c $$file | rapper -i turtle - "#" | \
# 		done > wReps.ttl; \
# 		fi;\
# 	)
#
# links.ttl.gz: wReps.ttl
# 	@# requires Apache Jena: arq
# 	arq --data wReps.ttl --query=link.sparql | tee links.ttl
