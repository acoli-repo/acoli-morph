all:
	for dir in */; do \
		echo $$dir;\
		if [ -e $$dir/Makefile ]; then \
			cd $$dir; \
			make;\
			cd ..;\
		fi;\
	done;\

clear:
	@echo "remove all generated files ... really [y/N]?" 1>&2
	@read test; \
		if echo $$test | egrep -i 'y' >/dev/null; then \
			for dir in */; do \
				echo $$dir;\
				if [ -e $$dir/Makefile ]; then \
					cd $$dir; \
					make clear;\
					cd ..;\
				fi;\
			done;\
		fi;\

refresh: clear all
