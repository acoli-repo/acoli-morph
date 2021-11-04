STYLESHEET = lexicon-transform.xslt
LEXICON = lexicon.xml
TMPFILE = $(LEXICON).tmp
SCHEMA = smor.rng
BUILDDIR = ../build

	
lexicon: basestems.xml adverbien.xml others.xml suff_stems.xml derivatives.xml prefixes.xml initials.xml aux_verbs.xml
	cat basestems.xml | sed '$$d' > $(TMPFILE)
	tail -n +4 adverbien.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 initials.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 others.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 derivatives.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 prefixes.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 aux_verbs.xml | sed '$$d' >> $(TMPFILE)
	tail -n +4 suff_stems.xml >> $(TMPFILE)
	xmllint $(TMPFILE) --relaxng $(SCHEMA) --format > $(LEXICON)
	xsltproc $(STYLESHEET) $(LEXICON) | python align.py >lexicon

.PHONY: distro

distro: $(LEXICON)
	cp $(SCHEMA) $(BUILDDIR)
	cp $(LEXICON) $(BUILDDIR)
	cp align.py $(BUILDDIR)
	cp $(STYLESHEET) $(BUILDDIR)
	cp -r legal*.html $(BUILDDIR)
	cp statistics.sh $(BUILDDIR)
	cp distro/* $(BUILDDIR)
	cp *.fst $(BUILDDIR)
	cp phon.a $(BUILDDIR)
	zip -r morphisto.zip $(BUILDDIR)
	mv morphisto.zip ..
	

.PHONY: clean

clean: 
	rm lexicon
	rm lexicon.xml
	rm $(BUILDDIR)/*
