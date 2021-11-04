# Morphological resources in OntoLex-Morph

idea:
- represent all major types of morphological resources in OntoLex
- inflectional morphology of an OntoLex entry (morphosyntactic features)
- derivational morphology of an OntoLex entry (morphological segmentation plus linguistic analysis)
- morphological rules

phenomena covered:
- [`uder/`](uder): derivation, sample conversion for German, includes bootstrapping of `morph:Morph`s and `morph:DerivationalRule`s
- [`unimorph/`](unimorph): inflection, sample conversion for German, includes bootstrapping of `morph:Morph`s and `morph:InflectionalRule`s
- [`germanet/`](germanet): compounding, German only, includes bootstrapping of `morph:Morph`s and `morph:CompoundingRule`s
- [`morphisto/`](morphisto): German SFST morphology, focus is the preservation of rules in OntoLex

OntoLex-Morph is still under development, so this is explorative work, mostly. The vocabulary may change.

At the moment, it is relatively unclear how replacements are to be specified. We have a consensus to use regular expressions for the purpose, but there is a single `morph:replacement` property only, and it seems to be an object property.
