# UniMorph

Schema and datasets for universal morphological annotation, OntoLex-Morph edition

Links:
- https://unimorph.github.io/
- https://unimorph.github.io/schema/

## OntoLex edition

To (re)build sample data, run

    $> make

## Experimental extensions

UniMorph does not provide explicit paradigms, so the converter just creates one
paradigm object per part-of-speech.

As an alternative, paradigms can also be bootstrapped from the combination of part
of speech and the end of the word. Such an induction is provided by `induce-paradigms.py`
and can be integrated into a refined conversion process. However, this is partially
language-specific and works only on languages that prefer derivation by suffix over
derivation by prefix.

For German, this boosts f-measure from 56% (use the most frequent paradigm per POS)
to 70% (use the paradigm with the longest string overlap and the same POS) on a 10%
random test set, mostly with improvements in precision. Recall stagnates below 60% in
all configurations, this is because our morpheme induction does not extend to forms whose
formation cannot be reduced to concatenating the canonical form (we don't have base forms,
here!) with a prefix and/or suffix.

Direct generation from UniMorph data is not recommended, because these contextual
statistics need to be calculated either explicitly (as here) or with other context-aware
techniques (e.g., the use of character embeddings). The Python module calculates them
from the raw file, but they can be equally calculated over the RDF graph.

## Source data

*excerpt from website*: https://unimorph.github.io/

The Universal Morphology (UniMorph) project is a collaborative effort to improve how NLP handles complex morphology in the world's languages. The goal of UniMorph is to annotate morphological data in a universal schema that allows an inflected word from any language to be defined by its lexical meaning, typically carried by the lemma, and by a rendering of its inflectional form in terms of a bundle of morphological features from our schema.

Plus, we're now available in a [Python package](https://pypi.org/project/unimorph/)!

	$> pip install unimorph

### UniMorph Events

-   [SIGMORPHON 2020 Shared     Task](https://sigmorphon.github.io/sharedtasks/2020/)
-   [SIGMORPHON 2019 Shared     Task](https://sigmorphon.github.io/sharedtasks/2019/)
-   [CoNLL--SIGMORPHON 2018 Shared     Task](https://sigmorphon.github.io/sharedtasks/2018/)
-   [CoNLL--SIGMORPHON 2017 Shared     Task](https://sigmorphon.github.io/sharedtasks/2017/)
-   [SIGMORPHON 2016 Shared     Task](https://sigmorphon.github.io/sharedtasks/2016/)

### Annotated Languages

141 languages have been annotated according to the
UniMorph schema. However, the information is often not complete.
