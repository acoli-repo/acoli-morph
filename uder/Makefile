all: src German

src:
	@echo retrieve source data
	git clone https://github.com/lukyjanek/universal-derivations src

src/py3env: src
	python3 -m venv src/py3env

German: src/py3env
	@echo build German sample data
	@# note that we cannot build everything at once, because some components require to download external resources beforehand
	@(cd src/de/DErivBase; make)
	@# build 
