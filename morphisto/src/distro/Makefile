STYLESHEET = lexicon-transform.xslt
LEXICON = lexicon.xml


lexicon: $(LEXICON)
	xsltproc $(STYLESHEET) $(LEXICON) | python align.py  > lexicon

.PHONY: clean

clean:
	rm lexicon

