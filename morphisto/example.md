# Example analyses

## "stehen" > "stehst"

`src/lexicon`:

    <Base_Stems>	steh,gestand	<V>	<base>	<nativ>	<VVPP-en>
    <Base_Stems>	steh,stand	<V>	<base>	<nativ>	<VVPastIndStr>
    <Base_Stems>	steh	<V>	<base>	<nativ>	<VVPres>
    <Base_Stems>	steh,stünd	<V>	<base>	<nativ>	<VVPastKonjStr>
    <Base_Stems>	stehend	<ADJ>	<base>	<nativ>	<AdjPos>
    <Deriv_Stems>	stehen,stand	<V>	<deriv>	<NSMasc_es_$e>
    <Pref_Stems>	stehen	<PREF>	<V>	<nativ>

`src/flexion.fst`:

    $FLEXION$ =   <>:<VVPres>		$VVPres$
    $VVPres$ =		{en}:{<>}	$VFlexPresReg$
    $VFlexPresReg$ =			$VFlexPres1$ | $VPres2Reg$ | $VPres3Reg$ | $VImpSg$
    $VFlexPres1$ =				$VPres1Reg$ | $VPresPlInd$ | $VPresKonj$ | $VImpPl$ | $VInfStem$
    $VPresPlInd$ =  {<+V><1><Pl><Pres><Ind>}:{<FB>en}       $V+(es)$ |\     % (wir) lieben, wollen, sammeln
                    {<+V><2><Pl><Pres><Ind>}:{<DEL-S>t}     $V+(es)$ |\     % (ihr) liebt, biet-e-t, sammelt
                    {<+V><3><Pl><Pres><Ind>}:{<FB>en}       $V+(es)$        % (sie) lieben, wollen, sammeln

    $V+(es)$ =      {/'s}:{'s}?             $V#$
    $V#$ = <>:<Low#>

`smor.fst`:

    $BASE$ = $TMP$ $FLEXION$

    $TMP$ = $S0$ | $S1$ | $Sx$

    $S0$ = $BDKStems$ $Suffs1$ || $SUFFFILTER$
    $S1$ = $P1$ $Suffs2$ || $SUFFFILTER$
    $Sx$ = $Quant$ ($BDKStems$ $QSuffs$ || $SUFFFILTER$)

    $BDKStems$ = $LEX$ || ($I$ [<Base_Stems><Deriv_Stems><Kompos_Stems>] $ANY$)

    $LEX$ = "lexicon"

Weird: `$FLEXION$` requires a final `-en` (in order to remove it), but if I read smor.fst right, then it only gets the base form (without `-en`). Can we assume that the replacement applies only if the precondition is met?

For the moment, we introduce a new lexicalForm subproperty: `baseForm`. This is similar to `canonicalForm`, but different in function, it represents a stem from which other forms can be generated, and this stem may be different from the lemma form found in a dictionary (as it is systematically for German, French, Russian and Bulgarian, for example, there the lemma form is one specific inflected form, e.g., German infinitive with "-en", Russian infinitive with "-it'" or "-at'" and Bulgarian first person  singular indicative present in "-am").

But as the morphology overgenerates (in fact, *every* morphology overgenerates), we should distinguish the output of the morphological forms from *attested* lexical forms, because they are not (unless we find other evidence). I suggest `morph:hypotheticalForm` as subproperty of `ontolex:lexicalForm` to represent generated forms.
Note that baseforms won't match any canonical or lexical form for German verbs. However, if hypothetical forms are generated (along with their features), these can be matched with other lexical forms, and then, lexical entries for base forms can be linked via their generated forms. (By matching, this also confirms the existence of hypothetical forms and justifies their upgrading.)

**Suggested model update**: By (ab)using `morph:InflectionType` for FST rules, one may wonder whether not to rename `morph:InflectionType` to `morph:InflectionRule` and the current `morph:InflectionRule` to `morph:Replacement`. Then, the terminology would be less confusing. But if this class is the counterpart of `morph:WordFormationRule`, then it should also carry `morph:example`.

## Modelling

### TBox

  morph:baseForm rdfs:subPropertyOf ontolex:lexicalForm.
  morph:hypotheticalForm rdfs:subPropertyOf ontolex:lexicalForm.

Note that we use `morph:isParadigmOf` for the inverse of `morph:hasParadigm`.

### "stehen" > "stehst"

  ## from lexicon: one entry per line
  :entry#151 a ontolex:LexicalEntry;
    morph:baseForm :base#151_steh, :base#151_gestand.
  :entry#152 a ontolex:LexicalEntry;
    morph:baseForm :base#151_steh.
    # we go on with the second

  # two different base forms for one lexical entry
  :base#151_steh a ontolex:Form;
    ontolex:writtenRep "steh".
  :base#151_gestand a ontolex:Form;
    ontolex:writtenRep "gestand".
  # the following form is not the same as the other steh thing, because it is from a different entry
  :base#152_steh a ontolex:Form;
    ontolex:writtenRep "steh".

  :entry#151 morph:paradigm :paradigm#VVPP-en.
  :entry#152 morph:paradigm :paradigm#VVPres.

  # we create a :paradigm# object for every PARADIGM value
  # we stipulate that a corresponding InflectionType must exist
  :paradigm#VVPres :morph:isParadigmOf :type#VVPres.

  ## from flexion.fst
  :type#VVPres a morph:InflectionType;
    morph:inflectionRule :rule#VVPres;
    morph:next :type#VFlexPresReg.
  :rule#VVPres a morph:InflectionRule;
    morph:replacement "s/en$//".

  :type#VFlexPresReg a morph:InflectionType;
    morph:inflectionRule :rule#VFlexPresReg;
    morph:next :type#VFlexPres1, :type#VPres2Reg, :type#VPres3Reg, :VImpSg.
  :rule#VFlexPresReg a morph:InflectionRule;
    morph:replacement "s/$//".

  :type#VFlexPres1 a morph:InflectionType;
    morph:inflectionRule :rule#VFlexPres1;
    morph:next :type#VPresPlInd. # and others
  :rule#VFlexPres1 a morph:InflectionRule;
    morph:replacement "s/$//".

  :type#VPresPlInd a morph:InflectionType;
    morph:inflectionRule :rule#VPresPlInd;
    morph:next :type#V%2B(es).
  :rule#VPresPlInd a morph:InflectionRule;
    morph:replacement "s/<+V><2><Pl><Pres><Ind>$/<DEL-S>t/".
    # problem here: the morphosyntactic features are *not* in the string, yet

  :type#V%2B(es) a morph:InflectionType;
    morph:inflectionRule :rule#V%2B(es);
    morph:next :type#V%23.
  :rule#V%2B(es) a morph:InflectionRule;
    morph:replacement "s/\/'s$/'s/".
    # problem here: /' is not initialized

  # problem: the tags are filtered out (and some transformations are applied, like <DEL-S> which will insert e before s if it follows a consonant)

  :type#V%23 a morph:InflectionType;
    morph:inflectionRule :rule#V%23.
    # no morph:next !
  :rule#V%23 a morph:InflectionRule;
    morph:replacement "s/$/<Low#>/".

### Generation

The rules (inflection types) cannot properly generate because we don't have the necessary start symbols (tags) in place nor do we get from a tagged string to a plain string to produce a form.
But they define a path from the paradigm to the last rule:

  :entry#151
    -hasParadigm->                 replacement  intermediate forms
      -isParadigmOf-> :type#VVPres [ s/en$// ]  (not applicable to base, hence *steh)
        -next-> :type#VFlexPresReg [ s/$// ]    (*steh)
        -next-> :type#VFlexPres1   [ s/$// ]    (*steh)
        -next-> :type#VPresPlInd   [ s/<+V><2><Pl><Pres><Ind>$/<DEL-S>t/ ]  (???)
         (not applicable, because the source string doesn't match,
         if they did, we end up with *steh<DEL-S>t)
        -next-> :type#V%2B(es)     [ s/\/'s$/'s/ ]                          (???)
        (not applicable because we don't support the /' syntax,
        I guess that means: "insert s after last >"
        With the current mapping to regular expressions, this isn't expressed either.
        If we did, we would end up with *steh<DEL-S>st [I guess])

We cannot transform `<DEL-S>` because we're not calling the generation rule. This is `$R13$` in `src/phon.fst`:

    % gewappn&t&st  ==> gewappnetst
    $R13$ = ((((c[hk])|[bdfgmp])n) <DEL-S> <=> e) & \
    	((<DEL-S>:e[dt]) <DEL-S> <=> <>)


Let's assume we start with a hypothetical form that provides us with the correct morphological features

  :entry#151 morph:hypotheticalForm :form#151_2_PL_Pres_Ind.
  :form#151_2_PL_Pres_Ind a ontolex:Form;
    lexinfo:person lexinfo:second;
    lexinfo:number lexinfo:plural;
    lexinfo:tense lexinfo:present;
    lexinfo:verbform lexinfo:indicative.

With lexinfo, we're stuck here, because it doesn't allow us to define a mapping from categories to tags.
But let's assume we have an OLiA annotation model.
In fact, we don't need it, we just need the hasTag property. Implicitly, this makes the form an instance of an OLiA concept.

  :form#151_2_PL_Pres_Ind
    olia:hasTag "<+V><2><Pl><Pres><Ind>".

The generation can then start by concatenating this tag with a base (but note there may be multiple bases).

If we do that, we have the following generation path (with intermediate results as indicated)

:form#151_2_PL_Pres_Ind                           [*...<+V><2><Pl><Pres><Ind>]
  <-hypotheticalForm- :entry#151
    -baseForm-> "steh"                            [*steh<+V><2><Pl><Pres><Ind>]
    -hasParadigm->                 replacement  intermediate forms
      -isParadigmOf-> :type#VVPres [ s/en$// ]    [*steh<+V><2><Pl><Pres><Ind>]
        (the replacement is not applicable, if we allow generation to ignore that for
        non-tag values, then, we keep the same string)
        -next-> :type#VFlexPresReg [ s/$// ]      [*steh<+V><2><Pl><Pres><Ind>]
        -next-> :type#VFlexPres1   [ s/$// ]      [*steh<+V><2><Pl><Pres><Ind>]
        -next-> :type#VPresPlInd   [ s/<+V><2><Pl><Pres><Ind>$/<DEL-S>t/ ]
                                                  [*steh<DEL-S>t]
        -next-> :type#V%2B(es)     [ s/\/'s$/'s/] [*steh<DEL-S>st]  (???)
         (generated only if we provide some implementation of the /' syntax)

With that, we're almost there, but we need another phase of surface generation.
That would be beyond OntoLex-Morph, but motivate a phonology/generation module.
We need something like this also for allomorphy.

For some words, we would have a string now that we can match against externally provided forms

**Note**: The replacement operation, and the left-to-right generation (insertion of `$` in replacements) is
most certainly incorrect, and it needs to be revised to account for the `/'` notation, at least.

**Note**: With the OLiA tag, we can use the hypothetical form and its link to the inflection type as the starting point of generation.
In fact, we don't need hypothetical forms then, but just a regular lexical form that does not have a writtenRep.
The writtenRep would be generated by the morphology.


## Revised Modelling

### TBox

  morph:baseForm rdfs:subPropertyOf ontolex:lexicalForm.

We don't use `morph:hypotheticalForm` anymore. this is just a lexicalForm without a writtenRep,
but with an `olia:hasTag` property.

We also don't use the paradigm information anymore, but just go directly from form to inflection type.

### "stehen" > "stehst"

  ## from lexicon: one entry per line
  :entry#151 a ontolex:LexicalEntry;
    morph:baseForm :base#151_steh, :base#151_gestand.
  :entry#152 a ontolex:LexicalEntry;
    morph:baseForm :base#151_steh.
    # we go on with the second

  # two different base forms for one lexical entry
  :base#151_steh a ontolex:Form;
    ontolex:writtenRep "steh".
  :base#151_gestand a ontolex:Form;
    ontolex:writtenRep "gestand".
  # the following form is not the same as the other steh thing, because it is from a different entry
  :base#152_steh a ontolex:Form;
    ontolex:writtenRep "steh".

  # we not create one form element for every target inflection
  # and we make it a blank node, because we don't know anything about it
  # in particular not which base it would take, if there is more than one
  # so we cannot give it a unique URI
  :entry#152 ontolex:lexicalForm
    [ a ontolex:Form;

      # grammatical information
      lexinfo:person lexinfo:second;
      lexinfo:number lexinfo:plural;
      lexinfo:tense lexinfo:present;
      lexinfo:verbform lexinfo:indicative;

      # we define the generation
      olia:hasTag "<+V><2><Pl><Pres><Ind>";
      morph:inflectionType :type#VVPres ] .

Together with the `morph:baseForm`(s) from the lexical entry, this is concrete
processing instruction from which can generate hypothetical forms (or, more precisely,
abstractions over these, because we don't do surface generation).

  ## add triples from flexion.fst
  ## all remains unchanged

**Note 1:** `olia:hasTag` originally had a different function, and used as a feature to match (parts of) tags.
However, this extension doesn't break its original semantics.
In fact, the related properties `olia:hasTagStartingWith` and `olia:hasTagEndingWith` may be even better
suited because these allow us to indicate where to put the grammatical information onto the base.
As there are no cardinality restrictions, we can also use both these properties to give the base a "prefix" and a "suffix".

**Note 2:** to use the base form and `olia:hasTag` in combination also allows us to add other kinds of strings to the base form.
In particular, we can add the mysterious `en` string that the `$VVPres$` rule presupposes but that is not in the lexicon (this rule actually starts with the canonical form, not with the base form, hence the mismatch).
This is very much a hack, though, and we should skip it from the current modelling.

  :entry#152 ontolex:lexicalForm
    [ a ontolex:Form;

      # grammatical information
      lexinfo:person lexinfo:second;
      lexinfo:number lexinfo:plural;
      lexinfo:tense lexinfo:present;
      lexinfo:verbform lexinfo:indicative;

      # we define the generation
      olia:hasTagEndingWith "<+V><2><Pl><Pres><Ind>en";
      morph:inflectionType :type#VVPres ] .

### Afterthoughts on paradigm and annotation model

We should maintain the paradigm element introduced above. This is because we have no links between lexical entry and inflection type if we do not provide all these hypothetical forms. However, if we just define
the annotation model and the paradigm, this is enough information to generate all hypothetical forms from there.

With this information, we can automatically flesh out the lexical entry by
- creating hypothetical forms for **all combinations** of
  - objects of baseForm (or a canonicalForm, depending on model and ruleset),
  - hasTag values from the annotation model,
  - objects of paradigm  
- following all generation paths to produce abstract forms (which may be identical with string forms)
- perform surface generation to produce string forms

This requires an annotation model that:
- provides tags (tag suffixes and prefixes) for each inflected form along with their lexinfo (or OLiA reference model) features
- temporary url for annotation model: `http://purl.org/acoli/acoli-morph/owl/morphisto#` under `annomodel.ttl`. To be integrated with OLiA.

### Minor updates

- we maintain the paradigm and `morph:isParadigmOf`, but this is created during dictionary creation, not during fst conversion, because not all states are valid paradigm identifiers, but only those that represent starting points for inflection.
- we link *the paradigm* with the OLiA annotation model, not the lexical entry. this is because different rule sets may operate on different symbols.
- for generation, we only need to provide a lexical entry with its base form (or canonical form -- default behaviour wold be to use the base form when provided and the canonical form otherwise) and with a paradigm, from the paradigm we then retrieve the OLiA model. However, this means we need to filter the possible tags against the features of a lexical entry. This may be a relatively loose fit, so that we end up with impossible combinations of values and rules. So, whether a certain feature combination really works for a given lexeme may become evident during the attempt to generate possible forms.
