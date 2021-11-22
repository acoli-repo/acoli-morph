# Morphological resources in OntoLex-Morph

idea:
- represent all major types of morphological resources in OntoLex
- inflectional morphology of an OntoLex entry (morphosyntactic features)
- derivational morphology of an OntoLex entry (morphological segmentation plus linguistic analysis)
- morphological rules

resources/phenomena covered:
- [`uder/`](uder): derivation, sample conversion for German, includes bootstrapping of `morph:Morph`s and `morph:DerivationalRule`s
- [`unimorph/`](unimorph): inflection, sample conversion for German, includes bootstrapping of `morph:Morph`s and `morph:InflectionalRule`s
- [`germanet/`](germanet): compounding, German only, includes bootstrapping of `morph:Morph`s and `morph:CompoundingRule`s
- [`morphisto/`](morphisto): German FST morphology, focus is the preservation of rules in OntoLex, also shows how to use SPARQL to bootstrap a regexp-based morphological generator from `morph:InflectionRule`s.
- [`linking/`](linking): `owl:sameAs` links across all aforementioned datasets

release:
- [`release/`](release): release of the interlined graph in binary (RDF-HDT) format

The repository contains the release data, to re-build from scratch, run

    $> make refresh

OntoLex-Morph is still under development, so this is explorative work, mostly. The vocabulary may change.

At the moment, OntoLex-Morph is capable of covering one-level morphologies, but not two-level morphologies. Morphisto is a two-level morphology for which we provide a reconstruction. The drop in performance in comparison to the native implementation is the omission of two-level morphology rules (i.e., filters and morphophonological processes that operate over "deep" morphology created in the first level)

## Multilingual extension

At the moment, we focus on German. However, the converters can be extended to other languages
more or less directly.
