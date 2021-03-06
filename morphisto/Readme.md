# Morphisto / SMOR

German morphological generator/analyzer
- SMOR: morphology
- Morphisto: lexicon

links:
- https://code.google.com/archive/p/morphisto/
- based on [SMOR](https://www.ims.uni-stuttgart.de/en/research/resources/tools/smor/), German SFST morphology; accessible after email request only, no longer separately distributed
- SMOR now bundled with the SFST release, see https://www.cis.uni-muenchen.de/~schmid/tools/SFST/ and https://github.com/santhoshtr/sfst

Disclaimer:
- OntoLex is limited (by design) to support context-free one-level morphologies only. As we generate sed-style replacements, it supports capturing groups, but no explicit variables. Also, from a two-level morphology like Morphisto/SMOR, it will only capture the first level ("deep generation") but not the second (morphophonological rules and filters, "surface generation").
- Two-level morphologies are a requirement that future OntoLex editions may address

## OntoLex-Morph edition

We convert the Morphisto lexicon and the inflection rules, but not the full (S)FST apparatus.
For encoding finite state automata in OntoLex-Morph, we use the `morph:InflectionType` element to represent states (nonterminals).
The `morph:next` property expresses the transition between states, the `morph:inflectionRule` provides the string replacement.

For triggering an inflection, an `ontolex:Form` needs to point to the (inflection type that represents the) start state.
However, this is problematic, because the Morphisto generation generates all possible forms from abstract concepts, so that this top-level state
is the POS of the lexical entry and the morphological features are generated along the way -- but not in an OntoLex-compliant way.

**Alternative**: So, instead, it would be better to make these top-level nodes an `ontolex:Paradigm` and to not specify indivdual forms.
Then, morphological features must be encoded explicitly as part of the inflection type (from which they could be transferred to the `ontolex:Form` as soon as it is generated.
In this case, the form would point to the *last* state that lead to its generation. However, it does have no trace of the full path, and if multiple paths terminate in the same state,
we lose any information on how we came from the paradigm to the morphological features.

Note that we have no formal notion of tags, but treat them as explicit substrings.
Also note that we do not support filters.

Note that the current OntoLex encoding of inflection rules is deficient because it does not allow us to define an end state.
By default, we would assume that we the path until no more `morph:next` properties are found.
But this leaves us without validation possibility and violates the Open World Assumption.

Finally, OntoLex-Morph does not provide filters. In FST grammars, these can be used in combination with an overgenerating grammar to produce valid output only. For OntoLex-Morph, we would have to postulate implicit filters, in using a corpus to limit generated output to attested forms.

Build with

    $> make

### discussion and vocabulary

We introduce the following new vocabulary elements:

    morph:baseForm rdfs:subPropertyOf ontolex:lexicalForm.

    morph:isParadigmOf # inverse of morph:hasParadigm to get from a morph:Paradigm to the morph:InflectionType  

    olia:hasTag, olia:hasTagStartingWith, olia:hasTagEndingWith # from OLiA

Moreover, for automatically generated forms, I introduce a new class `morph:HypotheticalForm` (or `ConstructedForm`?) as a subclass of `ontolex:Form`. We just need a way to mark them, and this seems to be more straight-forward than to encode it at the property.

See [example](example.md) for a discussion

For navigation from lexical entry to inflection type, it is VERY unfortunate that these properties have the same name, because we must disambiguate them via their object class

### deu/lexicon.ttl

contains the data converted from `src/lexicon`.
plus links to `deu/flexion.ttl` and `annomodel.ttl`.

links to the annotation model are currently added to the `morph:Paradigm` elements. This is sparser than doing that for every lexical entry, and it actually allows to combine different rule sets with different abbreviations to be applied to the same lexical entry (e.g., one that results from a merger).

See [structure](structure.md) for an analysis of the original structure of the lexicon file.

At the moment, we only capture base forms and their inflection. Derivation and composition are not covered, yet.

### deu/flexion.ttl

converted from `src/flexion.fst`

idea is to model FST states as `morph:InflectionRule`

note that we don't do surface generation or filtering, but we generate "abstract" morphology. This may be either identical with the surface string or it may contain special symbols that need to be replaced afterwards.
This final surface generation step is beyond OntoLex-Morph, but may be within a designated "transformation" module that may also cover, for example, transliteration problems.

Note that "paradigms" are not defined here, but in `deu/lexicon.ttl`, because the FST model cannot distinguish paradigm and non-paradigm states. The former are "root nodes" for generating forms, the latter are intermediate.

### annomodel.ttl

contains the OLiA annotation model needed for generating hypothetical forms from base forms. this bundles tags with lexinfo attribute-value pairs. To generate a (hypothetical) form, provide a lexical entry with an OLiA model, a base form (together, these generate the input to the transformer) and a paradigm (this defines the start state of the FST).

## Generation

With the current modelling of replacements, we can use SPARQL to generate sed or perl (or, with little more effort, Java, Python or even SPARQL) scripts that implement the rules, see `rule2sed.sparql`. Originally, this was directly executed by `sed`, but as this requires access to disk, we now read the sed script to Python and process it using `re.sub` (some escapes need to be undone). Note that the final removal of tags is heuristic, and, in particular, the morphophonological rules and filters (that would be triggered by these tags) are not covered. We thus add two extra rules to `rule2sed.sparql`: Put `*` in front of the form if the final form contains any tag, then remove all tags. When writing OntoLex output, this `*` is removed, but the generated form is marked as a `morph:HypotheticalForm`.

Try it with

    $> make test

As we do not include the morphophonological rules of Morphisto/SMOR, all generated forms are flagged as non-final/hypothetical (and marked with `*`). For such unconfirmed forms, we only return forms that differ from the base form. However, all forms are generated, but just suppressed from output.

We provide two rule extraction scripts:

- `rule2sed.sparql` is a best effort to disentangle all possible paths. However, this is relatively slow in execution and it takes about a minute to retrieve the `sed` scripts: For Morphisto, we have > 1000 rules, and these are combined with all possible OLiA tags that a lexical entry can have (up to 167, in loose mode), so we have up to 180.000 transformations per base form.
- `rule2sed-greedy.sparql` will create a single transformation for every paradigm. This is reasonably fast, but only generate on form per inflection type. However, as these represent FST states, they can potentially generate multiple outputs. With greedy rules, we have 268 rules, so only up to 45.000 transformations per base form.

### Sample output

    Aachen lexinfo:gender lexinfo:neuter; lexinfo:partOfSpeech lexinfo:commonNoun; lexinfo:partOfSpeech lexinfo:properNoun
    *Aachens lexinfo:case lexinfo:genitive; lexinfo:gender lexinfo:neuter; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun

    Aal lexinfo:gender lexinfo:masculine; lexinfo:partOfSpeech lexinfo:commonNoun
    *Aale lexinfo:case lexinfo:accusative, lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:accusative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:accusative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:dative, lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:dative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:dative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:genitive, lexinfo:nominative; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:genitive; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:genitive; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:nominative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
          lexinfo:case lexinfo:nominative; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun

    Adel lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
    *Adeles lexinfo:case lexinfo:genitive; lexinfo:gender lexinfo:masculine; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun

    Bildnis lexinfo:gender lexinfo:neuter; lexinfo:partOfSpeech lexinfo:commonNoun
    *Bildnise lexinfo:case lexinfo:accusative, lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:accusative; lexinfo:gender lexinfo:neuter; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:dative, lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:dative; lexinfo:gender lexinfo:neuter; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:genitive, lexinfo:nominative; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:genitive; lexinfo:gender lexinfo:neuter; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:genitive; lexinfo:number lexinfo:plural; lexinfo:partOfSpeech lexinfo:commonNoun
              lexinfo:case lexinfo:nominative; lexinfo:gender lexinfo:neuter; lexinfo:number lexinfo:singular; lexinfo:partOfSpeech lexinfo:commonNoun

    enth??ll lexinfo:partOfSpeech lexinfo:verb
    *enth??llt lexinfo:partOfSpeech lexinfo:verb; lexinfo:tense lexinfo:past; lexinfo:verbForm lexinfo:participle
              lexinfo:partOfSpeech lexinfo:verb; lexinfo:tense lexinfo:present; lexinfo:verbForm lexinfo:participle
              lexinfo:partOfSpeech lexinfo:verb; lexinfo:verbForm lexinfo:infinitive

    entkomm lexinfo:partOfSpeech lexinfo:verb; lexinfo:verbForm lexinfo:participle
    *entkommen lexinfo:partOfSpeech lexinfo:verb; lexinfo:tense lexinfo:past; lexinfo:verbForm lexinfo:participle
               lexinfo:partOfSpeech lexinfo:verb; lexinfo:tense lexinfo:present; lexinfo:verbForm lexinfo:participle

## Source

### SMOR / SFST

Stuttgart FST system, install on Ubuntu with `sudo apt-get install fst` or on Python with `pip install sfst`.
Contains a baseline grammar, but only a toy lexicon. This lexicon is provided by Morphisto.

Local installation needed for evaluation of the generated forms.

### Morphisto - FST-based Morphological Analyzer for German

excerpt from *https://code.google.com/archive/p/morphisto/*

Morphisto is a morphological analyzer and generator for German wordforms. The basis of Morphisto is the open-source SMOR morphology for the German language developed by the University of Stuttgart (GPL v2) for which a free lexicon is provided under the Creative Commons 3.0 BY-SA Non-Commercial license.

The Morphisto lexicon was originally developed at the [Institute for the German Language, Mannheim (Germany)](http://www.ids-mannheim.de) as part of the [TextGrid project](http://www.textgrid.de). This site hosts the new central place to go on the net for everything regarding Morphisto: Bugfixes and improvements, new feature, utilities, and getting in touch with the developers.

Morphisto requires as dependency the SFST toolkit available from the [University of Stuttgart](http://www.ims.uni-stuttgart.de/projekte/gramotron/SOFTWARE/SFST.html), as well as a computer running a contemporary Unix distribution (Ubuntu, Debian, OSX, you name it). If you want to compile your own Morphisto automaton a minimum of 8 GB RAM is highly recommended. However, this site also provides pre-compiled automatons. Windows users and the impatient ones can play with the Morphisto web-services available in the [TextGridLab](http://www.textgrid.de/beta.html) and hosted [here](http://ingrid.sub.uni-goettingen.de/cgi-bin/analyze.cgi).

*Project Information*
-   License: [GNU GPL v2](http://www.gnu.org/licenses/old-licenses/gpl-2.0.html)
-   Content License: [Creative Commons 3.0 BY-SA](https://code.google.com/archive/Creative%20Commons%203.0%20BY-SA)

### First Steps

excerpt from *https://code.google.com/archive/p/morphisto/wikis/FirstSteps.wiki*

In our experience, Morphisto newbies may experience some issues getting started. Once you have successfully installed the SFST tools and downloaded Morphisto, you will need to get ahold of a Morphisto FST automaton. The easiest way to go is to download the Morphisto build provided on the project site. The .a-suffix is meant to automatons in simple format, the .ca-suffix marks SFST automatons in compact format.

Once you have an automaton, you should have a look at one of these three tools that ship with SFST: * fst-mor * fst-infl * fst-infl2 * fst-compact fst-mor allows you to "chat" with the automaton: You enter a German word form and receive the result. _Enter_ switches between analysis respectively generation mode. fst-infl / fst-infl2 allow you to batch-process a text file containing a list of words. fst-compact can convert from the simple format to the compact one. There are some PDFs mainly written by Helmut Schmid which come with the SFST package. Whatever the Stuttgart people write about SMOR, will also apply to Morphisto. We hope that helps you to get started!

### Q/A
excerpt from *https://code.google.com/archive/p/morphisto/wikis/DeveloperCorner.wiki*

#### Open questions

-   Relation between Base- and KomposStem

    > > Despite of defining a KomposStem for a base entry, it is still possible to infer compounds from that base. `Alter<NN>:<>W:weisheit<+NN>:<><Fem>:<><Nom>:<><Sg>:<>` Should we define a special origin class for words which have a KomposStem and should not be used in compounds? `<BaseStem><Lemma>Alter</Lemma><Stem>Alter</Stem><Pos>NN</Pos><Origin>special</Origin><InfClass>NNeut_s_0</InfClass> <Frequency>10</Frequency> </BaseStem> <KomposStem><Upper>Alter</Upper><Lower>Alters</Lower><Pos>NN</Pos><Origin>nativ</Origin><Frequency>0</Frequency</KomposStem>` Is there an equivalent type of entry for derivations (e.g. DerivStem)?


> Comments by **CWRSimon**: Yes, there is the _DerivStem_ class, but honestly, I have never understood how to use it properly: `<Deriv_Stems>Pantomime:<><NN><deriv><fremd> <Deriv_Stems>Seku:?nde:<><NN><deriv><frei> <Deriv_Stems>Standard<NN><deriv><frei> <Deriv_Stems>Thema<>:t<NN><deriv><frei> <Deriv_Stems>divis<V><deriv><lang> <Deriv_Stems>erkunde:<>n:<><V><deriv><nativ> <Deriv_Stems>ertra:?g<V><deriv><nativ>` This would be a top-priority thing to ask Helmut Schmid... Regarding the first question: The idea to exclude base stems for which a compound stem has been defined appeals to me. However, would it still be possible to analyze _Zeitalter_ or _Zeitalterbestimmung_ then?

-   Derivation of complex verbs in different forms

    > > Comparing the analyses of "ernstmachen" und "ernstgemacht" shows that morphisto/SFST lacks ways to construct infinitives for (NN|ADJ)V constructions. The analysis with "ernst" as prefix seems to serve as a fallback but is (at least in my opinion and the one expressed in Fleischer/Barz) not correct. Two steps are two be taken:
    > >
    > > 1.  Find out of the construction of complex verbs from a free morphem and a base verb form is (still) a constructive one.
    > > 2.  If this is the case, add a rule similar to the past participle for infinitives. If not, add an entry for "ernstmachen" and similar forms to the lexicon and remove the means for constructing "ernst-ADJ-gemacht-V" from deko.fst.


### Resolved questions

**Prefix + Noun

> (Arbitrary)Combinations of prefix + noun are not possible in SMOR: `Absicht<+NN>:<><Fem>:<><Nom>:<><Sg>:<> Aufsicht<+NN>:<><Fem>:<><Nom>:<><Sg>:<> Hinsicht<+NN>:<><Fem>:<><Nom>:<><Sg>:<>` But: `Durch<OTHER>:<>S:sicht<+NN>:<><Fem>:<><Nom>:<><Sg>:<> Durch<OTHER>:<>D:durch<OTHER>:<>S:sicht<+NN>:<><Fem>:<><Nom>:<><Sg>:<>` **
>
> Solution a: Add productive noun prefixation in SMOR (deko.fst).
>
> Solution b: Add 'ab', 'auf' etc. as 'OTHER' to morphisto.
>
> Comments by **CWRSimon**: I do like the ideas, but I am wondering, whether prefixation is productive enough for German nouns in general: E.g., Morphisto already analyzes "Durchhund" and "Durchstuhl". Of course, one could argue that only nouns with a certain semantic feature can be prefixed with a prefix that embodies the same feature (e.g. Durch[+direction] and Gang[+direction] can form Durchgang). But then again, is prefixation really a process that applies to German nouns? I don't know what the literature says, but I would imagine the following: Prefixation is process that typically applies to verbs: durchgehen, durchsehen, hingehen, absehen, etc. And Durchgang, Aufsicht, Hinsicht, etc. are just the nominalizations of theses verbs. I do concede that I don't know, how to tell an FST-based morphology about German etymological wordformation processes....
>
> Comments by **wuerzner**: You are absolutely right: According to Fleischer/Barz, prefixation of nouns is a rare phenomenon. Nouns as 'Durchgang' should then be analysed as deverbal: `<CAP>durch<PREF>gehen<V><SUFF><+NN><Masc><Nom><Sg>` Are we able to implement that with SFST?
>
> Comments by **CWRSimon**: With FST-based technologies possibly, but not necessarily in the framework of Morphisto. What we need is a means of defining conversion rules from one POS class to another.
>
> Closing Remark by **wuerzner**: We can use

<DerivStem>

to implement this conversion. Have a look at the entry "fahren" in derivates.xml: The trick is to add the inflection class as origin and voil?? "Ausfahrt" can be traced to "fahren"! It also works with compositions like "Freifahrt".

**Verb participle to adjective conversion

> The following example shows that an adjective reading is only available for base verbs not for complex ones. `ver<PREF>suchen<+V><1><Sg><Past><Konj> ver<PREF>suchen<+V><1><Sg><Past><Ind> ver<PREF>suchen<+V><3><Sg><Past><Konj> ver<PREF>suchen<+V><3><Sg><Past><Ind> versuchen<+V><1><Sg><Past><Konj> versuchen<+V><1><Sg><Past><Ind> versuchen<+V><3><Sg><Past><Konj> versuchen<+V><3><Sg><Past><Ind> versuchen<V><PPast><SUFF><+ADJ><Pos><Masc><Nom><Sg><Sw> versuchen<V><PPast><SUFF><+ADJ><Pos><Fem><Nom><Sg> versuchen<V><PPast><SUFF><+ADJ><Pos><Fem><Akk><Sg> versuchen<V><PPast><SUFF><+ADJ><Pos><Neut><Nom><Sg><Sw> versuchen<V><PPast><SUFF><+ADJ><Pos><Neut><Akk><Sg><Sw> versuchen<V><PPast><SUFF><+ADJ><Pos><NoGend><Nom><Pl><St> versuchen<V><PPast><SUFF><+ADJ><Pos><NoGend><Akk><Pl><St>` For the (in principle superflous) full form entry of 'versuchen' but not for the derived form 'ver + suchen', adjective readings are generated. Assumedly, this is also a problem in 'deko.fst'.**
>
> Comments by **CWRSimon**: What exact wordform have you analyzed? _versuchen_ is not exactly a hypothetic attributive adjective form, only maybe a predicative one ("Dieses Angebot ist versuchen."). If one makes Morphisto analyze _versuchendes_, one will receive the analysis for an attributive adjective: `versuchen<V><PPres><SUFF><+ADJ><Pos><Neut><Akk><Sg><St/Mix> versuchen<V><PPres><SUFF><+ADJ><Pos><Neut><Nom><Sg><St/Mix> ver<PREF>suchen<V><PPres><SUFF><+ADJ><Pos><Neut><Akk><Sg><St/Mix> ver<PREF>suchen<V><PPres><SUFF><+ADJ><Pos><Neut><Nom><Sg><St/Mix>` But I agree that the internal workings of deko.fst are not very transparent and need to be examined in detail!
>
> Comments by **wuerzner**: The concrete form was 'versuchte' ('Der zun??chst versuchte Weg erwies sich als falsch.'). I confirm that everything is fine for 'versuchendes'. Do we have a bug here?
>
> Comments by **CWRSimon**: Possibly. Do you know the general rule for creating attribute adjectives from verbs? SMOR/Morphisto seems to use the Partizip-II form, because _vergesuchte_ works. Compare with _abgrasen_: It is possible to use _abgegraste_ as an adjective (_das abgegraste Feld_), but you cannote say _das abgraste Feld_ which is analogous to _versuchte_. That brings me to another complicated matter. Morphisto analyzes _abgraste_ as an inflected verb form of 'abgrasen' (_Ich abgraste das Feld_). That is BS, because it should actually be (_Ich graste das Feld ab_). But that matter gets us closer to parsing than mere morphological analysis...
>
> Closing Remark by **wuerzner**: It is possible to make use of the MorphMarker 'no-ge' to allow for the analysis of derived verb forms as past participle. Conversion to ADJ works if such an analysis is available.

### Flexionsklassen SMOR
from *https://code.google.com/archive/p/morphisto/wikis/SmorClasses.wiki*

Tags im SMOR-Lexikon und was sie bedeuten k??nnten....

`<NFem-Deriv>` feminine, gebunde Derivationsmorpheme ("-it??t","-heit", etc.) feminin, freie lexikalische Morpheme, die vermutlich nur in Verbindung stehen (Legion, Begabung)
`<NFem-a/en>` feminin, a/-en-Alternation: Veranda-Veranden, Agenda-Agenden, Tumba-Tumben
`<NFem-in>` Suffixmarkierung f??r feminine Substantiva auf "-in"
`<NFem-is/en>` feminin, is-en-Alternation:Amaryllis-Amaryllen
`<NFem-is/iden>` feminin, is-iden-Alternation: Meningitis-Meningiten
`<NFem-s/$sse>` feminin, -s/-ss-Alternation mit Umlaut im Plural, Nuss-> N??sse
`<NFem-s/sse>` feminin, -s/-ss-Alternation ohne Umlaut im Plural, Erlaubnis-Erlaubnisse
`<NFem-s/ssen>` feminin, -s/-ssen-Alternation, Stewarde??-Stewardessen
`<NFem/Pl>` Feminina, die im Plural nicht flektieren, aber durchaus eine Singular-Form als Lemma haben k??nnen: Workbenches, Lire, Gruften, Divas, etc.
`<NFem/Sg>` feminin, nur Singular: Malaria, Haggada
`<NFem_0_$>` feminin, keine Flexion im Singular, Umlautung im Plural Tochter-T??chter
`<NFem_0_$e>` feminin, keine Flexion im Singular, Umlautung+e im Plural, Magd-M??gde
`<NFem_0_e>` feminin, keine Flexion im Singular, e-Suffix im Plural, Peninsula-Peninsulae-Peninsulaen (DatPl)
`<NFem_0_en>` feminin, keien Flexion im Singular, -en-Suffix im Plura, freie und Derivationsmorpheme: Architektonik, Sekunde, -ur, -enz
`<NFem_0_n>` feminin, keine Flexion im Singular, -n-Suffix im Plural, freie und Derivationsmorpheme: Gabe-Gaben, Police-Policen, -ive, -ie, -se
`<NFem_0_s>` feminin, keine Flexion im Singular, -s-Suffix im Plural, Tonika-Tonikas, Zamba-Zambas
`<NFem_0_x>` feminin, Singular und Plural formidentisch, vermutlich f??r Singular- bzw. Pluralia-Tantum, Viktualien, Jeans, Brasil
`<N?/Pl_x>` geschlechtslos, Pluralia-Tantum, ohne Affixe, Trichogramma, Salmoniden, Memoiren
`<N?/Pl_0>` geschlechtslos, Pluralia-Tantum, mit Null-Endung, Leute-Leuten (DatPl), Umschweife-Umschweifen (DatPl)
`<NMasc-Adj>` maskulin, substantivierte Adjektive, der Zusp??tkommende
`<NMasc-es_e>` angeblich Anis,funktioniert aber nicht
`<NMasc-ns>` maskulin, -ns-Genitiv-Suffix, -n-Plural-Suffix, Buchstabe
`<NMasc-s/$sse>` maskulin, -es-Genitiv, -sse-Plural, Umlautung, Bass-B??sse
`<NSMasc-s/$sse>` wie oben, aber f??r Derivationsst??mme, z. B. Abg??sse, Abl??sse
`<NMasc-s/Sg>` maskulin, -es-Genitiv, nur Singular, Hass,Passus
`<NMasc-s/sse>` maskulin, -es-Genitiv, -sse-Plural, K??rbis-K??rbisse
`<NMasc-s0/sse>` maskulin, keine Genitivendung, -sse-Plural, Albatros, Primas
`<NMasc-us/en>` maskulin, Endung auf -us/-os, -ses-Genitiv, Mythos-Mythosses-Mythen, Algorithmus-Algorithmusses-Algorithmen
`<NMasc-us/i>` wie oben, nur mit -i-Plural, Intimus-Intimusses-Intimi
`<NMasc/Pl>` feste Pluralst??mme, nicht deklinierbar, keine Angabe zum Singular au??er Lemma, Topi, Switches, Signori
`<NMasc/Sg_0>` maskulin, Singularia Tantum ohne Genitivsuffix, Beelzebub, Pence, Reverend
`<NMasc/Sg_es>` maskulin, -es/-s-Genitiv mitsamt Dativ-e, nur Singularformen
`<NMasc/Sg_s>` maskulin, -s-Genitiv mitsamt Dativ-e, nur Singularformen, Salmiak, Weda, Yoga (bei den letzten beiden wird vermutlich durch andere Constraints Genitiv-s und Dativ-e verhindert)
`<NMasc_0_x>` maskulin, in Plural und Singular alle Formen identisch, Fonds
`<NMasc_en_e>` maskulin, Greif, aber keine Form analysierbar
`<NMasc_en_en>` maskulin, -en-Genitiv, -en-Plural, Bub, Konfirmand, Kalif
`<NMasc_es_$e>` maskulin, -es/-s-Genitiv, -e-Plural mit Umlaut, Dativ-e, Kardinal
`<NMasc_es_$er>` maskulin, -es/-e-Genitiv, -er-Plural mit Umlaut (sofern m??glich), Dativ-e, Leib (kein Umlaut m??glich), Mann-M??nner
`<NMasc_es_e>` maskulin, -es/-s-Genitiv, -e-Plural ohne umlaut, Dativ-e, Fjord, Dieb
`<NMasc_es_en>` maskulin, -es/-en-Genitiv, -e-Plural, Dativ-e, Psalm, Apostroph
`<NMasc_n_n>` maskulin, -n-Genitiv, -n-Plural, Rabe, Skalde
`<NMasc_s_$>` maskulin, -s-Genitiv, kein Plural-Suffix, Umlautung, Schnabel-Schn??bel-Schn??benln
`<NMasc_s_$x>` maskulin, -s-Genitiv, kein Plural-Suffix, im Plural stets gleiche Formen, also kein Dativ-Pl-n! Graben-Gr??ben
`<NMasc_s_0>` maskulin, -s-Genitiv, kein Plural-Suffix, aber Dativ-Plural ("Clinchn"!), Clinch, Triangel
`<NMasc_s_e>` maskulin, -s-Genitiv, -e-Plural, Bastard, Sarkophag
`<NMasc_s_en>` maskulin, -s-Genitiv, -en-Plural, Titans, Ph??notyp, Zeh
`<NMasc_s_n>` maskulin, -s-Genitiv, -n-Plural, See, Mogul
`<NMasc_s_s>` maskulin, -s-Genitiv, -s-Plural, Radscha, Samba
`<NMasc_s_x>` maskulin, Genitiv-s, ansonsten in Singular und Plural s??mtliche Formen identisch, Hoden, Vordersteven
`<NNeut-0/ien>` neutrum, -s-Genitiv, -ien-Plural, kein Dativ-e, Kleinod, Adverb
`<NNeut-Dimin>` neutrum, -s-Genitiv, im Plural stets gleiche Form, St??del
`<NNeut_Dimin>` B??rschlein, keine Form feststellbar
`<NNeut-Herz>` neutrum, Herz
`<NNeut-a/ata>` neutrum, -s-Genitiv, -ata-Plural, Klima, Schema
`<NNeut-a/en>` neutrum, -s-Genitiv, -en-Plural, Drama-Dramas-Dramen
`<NNeut-on/a>` neutrum, -s-Genitiv, -a-Plural, Heroon-Heroons-Heroa
`<NNeut-s/$sser>` neutrum, -es-Genitiv, -sser-Plural mit Umlaut, Fa??
`<NNeut-s/sse>` neutrum, -es-Genitiv, -sse-Plural , Trumpfas-Trumpfasse-Trumpfassen
`<NNeut-um/a>` -s-Genitiv, -a-Plural, Unikum-Unika, Verbum-Verba
`<NNeut-um/en>` -s-Genitiv, -en-Plural, Album-Alben, Memorandum-Memoranden
`<NNeut/Pl>` neutrum, Pluralform, stets gleich
`<NNeut/Sg_0>` kein Plural, keine Genitiv-Endung, Pankreas, Tipitaka
`<NNeut/Sg_en>` kein Plural,GenDatAkk Sg. auf -en
`<NNeut/Sg_es>` kein Plural, -es/-s-Genitiv, Dativ-e m??glich,Gelb, Sandwich
`<NNeut/Sg_s>` kein Plural, nur -s-Genitiv, Dativ-e nicht m??glich, Manna, Olympia
`<NNeut_0_x>` indeklinierbar, in Sg. und Pl. alle Formen gleich, Penthouse
`<NNeut_es_$e>` -es/s-Genitiv, -e-Plural mit Umlautung, Dativ-Plural m??glich, Dativ-e, Flo??
`<NNeut_es_$er>` -es/-s-Genitiv, -er-Plural mit Umlaunt, Dativ-Plural m??glich, Dativ-e, Grab
`<NNeut_es_e>` -es/-s-Genitiv, -e-Plural, Dativ-Plural m??glich, Dativ-e, Oxyd, Sieb
`<NNeut_es_en>` -es/-s-Genitiv, -en-Plural, Dativ-Plural m??glich, Dativ-e, Etikett
`<NNeut_es_er>` -es/-s-Genitiv, -er-Plural, Dativ-Plural m??glich, Dativ-e, Weib
`<NNeut_s_$>` -s-Genitiv, kein Dativ-e, Dativ Plural m??glich, Plural nur mit Umlautung, Wasser
`<NNeut_s_0>` -s-Genitiv, kein Dateiv-e, Dativ-Plural m??glich, Plural wie Grundform, immer gleich, Getriebe, Leasing
`<NNeut_s_e>` -s-Genitiv, kein Dativ-e, Dativ-Plural m??glich, Pluralstamm auf -e, Insektizidm Zynid, Surfboard
`<NNeut_s_en>` -s-Genitiv, kein Dativ-e, -en-Plural, Apokryph, Juwel
`<NNeut_s_n>` -s-Genitiv, kein Dativ-e, -n-Plural, Ende, Interesse
`<NNeut_s_s>` -s-Genitiv, kein Dativ-e, -s-Plural, kein Dativ Plural, Labda, A, Omega
`<NNeut_s_x>` -s-Genitiv, kein Dativ-e, Plural wie Grundform, immer gleich, Amen, Leasing, Sp??tzle
`<Name-Fem_0>` weibl. Name, keine Flexionsendung, kein Plural, Andromeda, Seine
`<Name-Fem_s>` weibl. Name, -s-Genitiv, kein Plural, Helen
`<Name-Invar>` nichts m??glich
`<Name-Masc_0>` mask. Name, keine Flexionsendung, kein Plural, Wienerwald
`<Name-Masc_s>` mask. Name, -s-Genitiv, kein Plural, Balkan
`<Name-Neut_0>` neut. Name, keine Flexionsendung, kein Plural, Florenz
`<Name-Neut_s>` neut. Name, -s-Genitiv, kein Plural, Amerika
`<Name-Pl_0>` keine FLexionsendung au??er Dativ-Plural, nur Plural-Stamm, NoGender, Niederlande
`<Name-Pl_x>` keine FLexionsendung, nur Plural-Stamm, NoGender, Seychellen Maskulina: Dativ-e nur bei -es-Genitiv m??glich wie es aussieht Dativ-Plural-n wird nach M??glichkeit automatisch hinzugef??gt
`<Adj$>` regelm????ige Steierung mit Umlautung, arg
`<Adj$e>` regelm????ige Steigerung mit Umlautung und e-Einschub im Superlativ
`<Adj+(e)>` regelm????ige Steigerung mit evtl. e-Einschub, abhold, antik
`<Adj+>` regelm????ige Steigerung ohne Ged??ns, farbig
`<Adj+Lang>` Sprachadjektiv: afrikanisch, deutsch
`<Adj+e>` regelm????ige Steigerung mit e-Einschub: los
`<Adj-el/er>` regelm????ige Steigerung f??r Adjektive auf -el und -er
`<Adj0-Up>` keine Ahnung, aber nur in geographischen Lemmatan
`<Adj0>` keine Steigerung, keine Flexion
`<AdjComp>` spezieller Komparativ
`<AdjNN>` recht, schuld, whatever....
`<AdjNNSuff>` ""
`<AdjPos>` nur Positivform
`<AdjPosAttr>` nur Positivform mit attributivem Gebrauch
`<AdjPosPred>` nur Positivform mit pr??dikativem Gebrauch
`<AdjPosSup>` nur Positiv- und Superlativformen
`<AdjSup>` Superlativstamm
`<Adj~+e>` ba??, basser, bassesten
`<Adv>` Adverb, circa
`<Base_Stems>`
`<CARD,DIGCARD,NE>`
`<CARD,NN>`
`<CARD>`
`<Circp>`
`<DIGCARD>`
`<Deriv_Stems>`
`<FB>`
`<FamName_0>`
`<FamName_s>`
`<Ge-Nom>`
`<Initial>`
`<Intj>`
`<Kompos_Stems>`
`<Konj-Inf>`
`<Konj-Kon>`
`<Konj-Sub>`
`<Konj-Vgl>`
`<NE,NN,V>`
`<NE,NN>`
`<NE>`
`<NGeo-$er-Adj0-Up>`
`<NGeo-$er-NMasc_s_0>`
`<NGeo-$isch-Adj+>`
`<NGeo-0-Adj0-Up>`
`<NGeo-0-NMasc_s_0>`
`<NGeo-0-Name-Fem_0>`
`<NGeo-0-Name-Masc_s>`
`<NGeo-0-Name-Neut_s>`
`<NGeo-a-Name-Fem_s>`
`<NGeo-a-Name-Neut_s>`
`<NGeo-aner-Adj0-Up>`
`<NGeo-aner-NMasc_s_0>`
`<NGeo-anisch-Adj+>`
`<NGeo-e-NMasc_n_n>`
`<NGeo-e-Name-Fem_0>`
`<NGeo-e-Name-Neut_s>`
`<NGeo-ei-Name-Fem_0>`
`<NGeo-en-Name-Neut_s>`
`<NGeo-er-Adj0-Up>`
`<NGeo-er-NMasc_s_0>`
`<NGeo-erisch-Adj+>`
`<NGeo-ese-NMasc_n_n>`
`<NGeo-esisch-Adj+>`
`<NGeo-ianer-NMasc_s_0>`
`<NGeo-ianisch-Adj+>`
`<NGeo-ien-Name-Neut_s>`
`<NGeo-ier-NMasc_s_0>`
`<NGeo-isch-Adj+>`
`<NGeo-istan-Name-Neut_s>`
`<NGeo-land-Name-Neut_s>`
`<NGeo-ner-Adj0-Up>`
`<NGeo-ner-NMasc_s_0>`
`<NGeo-nisch-Adj+>`
`<NN,V>`
`<NN>`
`<NSFem_0_en>`
`<NSFem_0_n>`
`<NSMasc-s/$sse>`
`<NSMasc_es_$e>`
`<NSMasc_es_e>`
`<NSNeut_es_e>`
`<Name-Invar>`
`<Name-Pl_0>`
`<Name-Pl_x>`
`<NoDef>`
`<NoHy>`
`<ORD>`
`<OTHER>`
`<PREF>`
`<Postp-Akk>`
`<Postp-Dat>`
`<Postp-Gen>`
`<Pref/Adj>`
`<Pref/Adv>`
`<Pref/N>`
`<Pref/ProAdv>`
`<Pref/Sep>`
`<Pref/V>`
`<Pref_Stems>`
`<Prep-Akk>`
`<Prep-Dat>`
`<Prep-Gen>`
`<Prep/Art-m>`
`<Prep/Art-n>`
`<Prep/Art-r>`
`<Prep/Art-s>`
`<ProAdv>`
`<Ptkl-Adj>`
`<Ptkl-Ant>`
`<Ptkl-Neg>`
`<Ptkl-Zu>`
`<QUANT>`
`<SS>`
`<SUFF>`
`<Simplex>`
`<Suff_Stems>`
`<UL>`
`<V>` Verb
`<VAImpPl>` Hilfsverb, Imperativ Plural, Stamm
`<VAImpSg>` Hilfsverb, Imperativ Singular, Stamm
`<VAPastKonj2>` Hilfsverb, Konj. II., Stamm
`<VAPres1/3PlInd>` Hilfsverb, 1. und 3. Pers. Plural Indikativ
`<VAPres1SgInd>` Hilfsverb, 1. Pers. Sg. Indikativ
`<VAPres2PlInd>` Hilfsverb, 2. Pers. Pl. Pr??sens Indikativ
`<VAPres2SgInd>` Hilfsverb, 2. Pers. Sg. Pr??sens Indikativ
`<VAPres3SgInd>` Hilfsverb, 3. Pers. Sg. Pr??sens Indikativ
`<VAPresKonjPl>` Hilfsverb, Konj. I. Plural, Stamm
`<VAPresKonjSg>` Hilfsverb, Konj. I. Singular, Stamm
`<VInf+PPres>` Infinitiv und Partizip I, haben
`<VInf>` Infinitiv, sein
`<VMPast>`
`<VMPastKonj>`
`<VMPresPl>`
`<VMPresSg>`
`<VPPast>` Partizip II, getan, geworden
`<VPPres>` Partizip I, tuend
`<VPastIndReg>` Auxiliarverb, Past, Indikativ, schwach, hatte
`<VPastIndStr>` Auxiliarverb, Past, Indikativ, stark, tat
`<VPastKonjStr>` Auxiliarverb, stark, Konj.II, t??t
`<VPresKonj>` Auxiliarverb, Konj.I, habe
`<VPresPlInd>` Auxiliarverb,
`<VVPP-en>` Past Participle mit -en, Stamm
`<VVPP-t>` Past Participle mit -t, Stamm
`<VVPastIndReg>` Vollverb, Vergangenheit, Indikativ, schwaches Verb, wuss
`<VVPastIndStr>` Vollverb, Vergangenheit, Indikativ, starkes Verb, traf
`<VVPastKonjReg>` Vollverb, Vergangenheit, Indikativ, schwaches Verb, w??ss
`<VVPastKonjStr>` Vollverb, Vergangenheit, Konjunktiv, starkes Verb, tr??f
`<VVPastStr>` Vollverb, Vergangenheit, alle Modi, starkes Verb, schrie
`<VVPres1+Imp>` Vollverb, Pr??sens, Indikativ und Imperativ, grab
`<VVPres1>` Vollverb, Pr??sens, 1.Sg, Indikativ, nehm, les
`<VVPres2+Imp0>` Vollverb, 2./3. Sg. Pr??sens und Imperativ Sg., tritt
`<VVPres2+Imp>` Vollverb, 2. Sg Pr??sens und Imperativ Sg, Stamm, befiehl
`<VVPres2>` Vollverb, 2. Sg., Stamm autof??hr, gr??b
`<VVPres2t>` Vollverb, 2./3.Sg, h??lt
`<VVPres>` Vollverb, schwach, Pr??sens, schreib
`<VVPresPl>` Vollverb, schwach, Plural-Stamm, wissen
`<VVPresSg>` Vollverb, schwach, Singular-Stamm, wei??
`<VVReg-el/er>` Infinitivstamm schwache Verben mit el/er-Endung, doubeln
`<VVReg>` Infintivstamm schwache Verben, verausgaben
`<WAdv>`
`<base>`
`<d>`
`<deri>`
`<deriv>`
`<frei,fremd,gebunden,kurz>`
`<frei,fremd,gebunden,lang>`
`<frei,fremd,gebunden>`
`<frei,fremd,kurz>`
`<frei,fremd,nativ>`
`<frei,gebunden,kurz,lang>`
`<frei,gebunden,lang>`
`<frei,gebunden>`
`<frei,lang>`
`<frei,nativ>`
`<frei>`
`<fremd,klassisch,nativ>`
`<fremd,nativ>`
`<fremd>`
`<ge>`
`<gebunden>`
`<klassisch,nativ>`
`<klassisch>`
`<kompos>`
`<kurz>`
`<lang>`
`<n>`
`<nativ>`
`<prefderiv,simplex,suffderiv>`
`<prefderiv,simplex>`
`<simplex,suffderiv>`
`<simplex>`
`<suffderiv>`
`<~n>`
`<ABK>`
`<ADJ,CARD,NN,V>`
`<ADJ,CARD>`
`<ADJ,NE,NN>`
`<ADJ,NN,V>`
`<ADJ,NN>`
`<ADJ>`
`<ADV,NE,NN,V>`
`<ADV>` `<Abk_ADJ>`
`<Abk_ADV>`
`<Abk_ART>`
`<Abk_DPRO>`
`<Abk_KONJ>`
`<Abk_NE-Low>`
`<Abk_NE>`
`<Abk_NN-Low>`
`<Abk_NN>`
`<Abk_PREP>`
`<Abk_VPPAST>`
`<Abk_VPPRES>`
