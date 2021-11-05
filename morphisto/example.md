# Example analyses

"stehen" > "stehst"

    lexicon:
    <Base_Stems>	steh,gestand	<V>	<base>	<nativ>	<VVPP-en>
    <Base_Stems>	steh,stand	<V>	<base>	<nativ>	<VVPastIndStr>
    <Base_Stems>	steh	<V>	<base>	<nativ>	<VVPres>
    <Base_Stems>	steh,stünd	<V>	<base>	<nativ>	<VVPastKonjStr>
    <Base_Stems>	stehend	<ADJ>	<base>	<nativ>	<AdjPos>
    <Deriv_Stems>	stehen,stand	<V>	<deriv>	<NSMasc_es_$e>
    <Pref_Stems>	stehen	<PREF>	<V>	<nativ>

    flexion.fst:
    $FLEXION$ =   <>:<VVPres>		$VVPres$
    $VVPres$ =		{en}:{<>}	$VFlexPresReg$
    $VFlexPresReg$ =			$VFlexPres1$ | $VPres2Reg$ | $VPres3Reg$ | $VImpSg$
    $VFlexPres1$ =				$VPres1Reg$ | $VPresPlInd$ | $VPresKonj$ | $VImpPl$ | $VInfStem$
    $VPresPlInd$ =  {<+V><1><Pl><Pres><Ind>}:{<FB>en}       $V+(es)$ |\     % (wir) lieben, wollen, sammeln
                    {<+V><2><Pl><Pres><Ind>}:{<DEL-S>t}     $V+(es)$ |\     % (ihr) liebt, biet-e-t, sammelt
                    {<+V><3><Pl><Pres><Ind>}:{<FB>en}       $V+(es)$        % (sie) lieben, wollen, sammeln

    smor.fst:
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
