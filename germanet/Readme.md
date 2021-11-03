# GermaNet, compounds

GermaNet is a proprietary resource for lexical semantics in German, but its list of compound words is freely available from [University Tübingen](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/description/compounds/#c1081926) and used as a basis for modelling compounds here.

## Composition in GermaNet

*excerpt from [website](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/description/compounds/#c1081926)*

Composition is a very productive word formation process in German. For many applications, it is helpful to have information about the parts of the compound, as usually the semantic interpretation is based on the meaning of its parts. In GermaNet, nominal compounds are therefore split into their constituent parts, i.e., modifier and head. This splitting identifies the immediate constituents at each level of analysis and thus reflects the recursive nature of compounds that have more than two constituent parts such as *Autobahnanschlussstelle*('motorway junction'). The immediate constituents of this compound are *Autobahn* and *Anschlussstelle*, with the first constituent then splitting further into *Auto* and *Bahn* and the second constituent further split into *Anschluss* and *Stelle*.

What makes compound splitting for German a challenging task is the fact that compounding is not always simple string concatenation, but often involves the presence of intervening linking elements or the elision of word-final characters in the modifier constituent of a compound ([Henrich & Hinrichs, 2011](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/publications/)). In GermaNet, all modifiers are lemmatized and if a modifier is ambiguous with respect to its word class (due to conversion), both possibilities are specified:

-   Laufschuhe: lauf- (en) \[verb\] and (der) Lauf \[noun\]
-   Baustelle: bau- (en) \[verb\] and (der) Bau \[noun\]

Compound splitting in GermaNet is supported by an automatic algorithm, which combines several individual compound splitters. Please see the [referenced paper below](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/description/compounds/#c1081929) for more information on the automatic splitting. All automatically split compounds are manually post-corrected and enriched with relevant properties before they are inserted into GermaNet.

### Properties

The following properties are specified for modifiers and/or heads:

\
**Abbreviation**

If one part of the compound is an abbreviation, it is labelled
as *Abkürzung*.

Examples:

::: table-rwd
::: table-rwd__overflow
  ----------- -------------------- -------------------
  Compound    Modifier             Head
  SIM-Karte   SIM (abbreviation)   Karte
  ISO-Norm    ISO (abbreviation)   Norm
  Bonus-CD    Bonus                CD (abbreviation)
  ----------- -------------------- -------------------
:::
:::

\
**Affixoid**

Affixoids are morphemes with a special status between bound and free
morphemes. As they have a clearly assigned meaning, it makes sense to
split the respective words. The bound morpheme is labelled
as *Affixoid*.

Examples:

  ------------------ -------------------- -----------
  Compound           Modifier             Head
  Grundfrage         grund (affixoid)     Frage
  Riesenchance       riesen (affixoid)    Chance
  Hauptsaison        haupt (affixoid)     Saison
  Generalschlüssel   general (affixoid)   Schlüssel
  ------------------ -------------------- -----------

\
**Foreign Word**

If one part (or more) of the compound is not a German word, it is
labelled as *Fremdwort*. Note that those constituents which are borrowed
words but are nowadays used as loanwords defined in a standard German
dictionary (such as *Duden*) are not considered as foreign words in
GermaNet (e.g. *Drink* and *Pool *in the examples below).

Examples:

  -------------- ------------------------- -------
  Compound       Modifier                  Head
  Longydrink     long (foreign word)       Drink
  Swimmingpool   swimming (foreign word)   Pool
  Logdatei       log (foreign word)        Datei
  -------------- ------------------------- -------

\
**Konfix**

The label *Konfix* refers to a word which is borrowed from a foreign
language, in many cases from Latin or Greek, and whose meaning stems
from that particular language. *Konfixes* are bound morphemes, but in
opposition to all other affixes two *Konfixes* can be combined to form a
so-called *Konfixkompositum*. Those *Konfixkomposita* are not split in
GermaNet, whereas compounds existing of a *Konfix* and a native word are
split.

Examples:
  ------------ ---------------- --------
  Compound     Modifier         Head
  Milligramm   milli (Konfix)   Gramm
  Zentimeter   zenti (Konfix)   Meter
  Monokultur   mono (Konfix)    Kultur
  ------------ ---------------- --------

\
**Opaque Morpheme**

Modifiers whose meaning is not transparent any more without considering
the etymology of the word are labelled with the property *opaques
Morphem*.

Examples:

  ------------ ------------------------- ---------
  Compound     Modifier                  Head
  Himbeere     Him (opaque morpheme)     Beere
  Karfreitag   Kar (opaque morpheme)     Freitag
  Sintflut     Sint (opaque morpheme)    Flut
  Lebkuchen    Leb (opaque morpheme)     Kuchen
  Elfenbein    Elfen (opaque morpheme)   Bein
  ------------ ------------------------- ---------

\
**Proper Name**

If the whole compound is a named entity, it is not split in GermaNet. If
only the modifier is a proper name, the compound is split and the
label *Eigenname* is added to the modifier.

Examples:

  ----------------- ----------------------- -----------
  Compound          Modifier                Head
  Hubbleteleskop    Hubble (proper name)    Teleskop
  Wertherstimmung   Werther (proper name)   Stimmung
  Hiobsbotschaft    Hiob (proper name)      Botschaft
  ----------------- ----------------------- -----------

\
**Virtual Word Form**

Virtual word forms, labelled as *Virtuelle Bildung*, are regularly built
according to existing word formation rules. However, they do not exist
in isolation, but only as part of a compound.

Examples:

  --------------- ---------- -----------------------------
  Compound        Modifier   Head
  Einflussnahme   Einfluss   Nahme (virtual word form)
  Fragesteller    Frage      Steller (virtual word form)
  Farbgebung      Farbe      Gebung (virtual word form)
  --------------- ---------- -----------------------------

\
**Word Group**

Modifiers consisting of a phrase are marked as *Wortgruppe* and the
parts of the phrase are annotated as the modifier.

Examples:

  ------------------------ ------------------------------ -------------
  Compound                 Modifier                       Head
  Dreiwege-Katalysator     drei Weg (word group)          Katalysator
  Nacht-und-Nebel-Aktion   Nacht und Nebel (word group)   Aktion
  Pro-Kopf-Einkommen       pro Kopf (word group)          Einkommen
  ------------------------ ------------------------------ -------------

The following table gives an overview of the constituent parts of a
compound (i.e. modifier and head) and the corresponding properties that
are annotated for each constituent in GermaNet:

  ------------------- ---------- ------
  Property            Modifier   Head
  Abbreviation        x          x
  Affixoid            x          x
  Foreign Word        x          x
  Konfix              x           
  Opaque Morpheme     x          x
  Proper Name         x           
  Virtual Word Form              x
  Word Group          x           
  ------------------- ---------- ------

### Download

In addition to the information described above that is included in GermaNet (since release 8.0), a list of split compounds with their modifier(s) and head is freely available for download:

-   GermaNet v16.0 (2021): list of 106780 [split nominal    compounds](https://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet16.0.txt)
-   GermaNet v15.0 (2020): list of 98905 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet15.0.txt)
    (Updated June 15, 2020, [with    corrections](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet15.0_modified-2020-06-15.txt))
-   GermaNet v14.0 (2019): list of 91106 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet14.0.txt)
-   GermaNet v13.0 (2018): list of 82309 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet13.0.txt)
-   GermaNet v12.0 (2017): list of 74990 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet12.0.txt)
-   GermaNet v11.0 (2016): list of 66059 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet11.0_modified-2017-02-16.txt)     (v11.0: Updated Feb. 16, 2017)
-   GermaNet v10.0 (2015): list of 54569 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet10.0.txt)
-   GermaNet v9.0 (2014): list of 54759 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet9.0.txt)
-   GermaNet v8.0 (2013): list of 40437 [split nominal    compounds](http://www.sfs.uni-tuebingen.de/GermaNet/documents/compounds/split_compounds_from_GermaNet8.0_modified-2013-06-12.txt)\    (v8.0: Original list released on May 31, 2013, updated on June 12,    2013.)

The list of compound data is free for academic research as defined in GermaNet\'s [academic research licence agreement](https://uni-tuebingen.de/en/faculties/faculty-of-humanities/departments/modern-languages/department-of-linguistics/chairs/general-and-computational-linguistics/ressources/lexica/germanet/licenses/). For any other intended purposes, please contact the maintainers.

The format of these split compounds is one compound per line: first the compound itself, then a \<tab> space, then the modifier (in case of two modifiers, these are separated by the pipe (\|) symbol), then a \<tab> space again, and finally the head. For example:

*Apfelbaum      Apfel   Baum\
Goldmünze     Gold   Münze\
Laufband       laufen\|Lauf     Band*

### Reference

The following paper describes the automatic compound splitting that is performed before the manual post-correction. If you want to use the split compounds in the context of scientific or research work, please refer to the paper:

**Verena Henrich and Erhard Hinrichs**: [Determining Immediate Constituents of Compounds in GermaNet](http://www.aclweb.org/anthology/R11-1058){.external-link}. In Proceedings of Recent Advances in Natural Language Processing (RANLP 2011), Hissar, Bulgaria, September 2011, pp. 420-426.  
