# Structure of lexicon files

`src/lexicon`:
- "tags": *some* columns enclosed by `<...>`, note that the symbol `<>` used as part of a form definition, is not considered a tag, but as a part of the form string
- between "tags" can be free text, this is the actual primary data
- below, we count columns as a linear sequence of tags and non text

## col 1: ENTRY_TYPE

values sorted by frequency

`<Base_Stems>`
`<ge>`
`<NoHy>`
`<Suff_Stems>`
`<Pref_Stems>`
`<Kompos_Stems>`
`<Deriv_Stems>`
`<NoDef>`
`<Initial>`
`<QUANT>`

## entry types

There is no general pattern for the structure of entry patterns, but each kind of entry has a different structure.

### Deriv_Stems

This seems to be for handling stem alternations in derivation.

1. ENTRY_TYPE: `<Deriv_Stems>`
2. FORM: e.g., "Chaos:t" (to generate both "Chaos" and "Chaot")
3. BASE_POS: `<ADJ>`, `<NE>`, `<NN>`, `<V>`
4. RULE_TYPE: `<deriv>`
5. META: `<frei>`, `<fremd>`, `<gebunden>`, `<kurz>`, `<lang>`, `<nativ>`, `<NSFem_0_en>`, `<NSFem_0_n>`, `<NSMasc_es_$e>`, `<NSMasc_es_e>`, `<NSMasc-s/$sse>`, `<NSNeut_es_e>`

### Pref_Stems

1. ENTRY_TYPE: `<Pref_Stems>`
2. FORM: e.g., "para"
3. ???: `<PREF>`
4. BASE_POS: `<ADJ>`, `<NE>`, `<NN>`, `<V>`
5. META: `<fremd>`, `<fremd,klassisch,nativ>`, `<klassisch>`, `<klassisch,nativ>`, `<nativ>`, `<nativ,fremd>`

Note: `<PREF>` marks where BASE_POS entries begin, but these may occupy more than one column, if they do, all columns except for the last one (which is META) will contain *alternative BASE_POSes*. There can be up to three. If this is not respected, you'll see POS tags `<NN>` and `<V>` in META columns.

### Base_Stems

1. ENTRY_TYPE: `<Base_Stems>`
2. FORM: e.g., `Mini`, `Uni`
3. POS: `<ABK>`, `<ADJ>`, `<ADV>`, `<NE>`, `<NN>`, `<OTHER>`, `<V>`
4. RULE_TYPE: `<base>`
5. META: `<frei>`, `<fremd>`, `<klassisch>`, `<nativ>`
6. FEATS: e.g., `<NFem_0_s>`

The META criterion includes information about either origin `<nativ>`, `<fremd>` or morphological patterns (`frei`, `gebunden`). Not clear how this is internally used.

### Suff_Stems

1. ENTRY_TYPE: "`<Suff_Stems>`"
2. RULES (?): `<prefderiv,simplex>`, `<prefderiv,simplex,suffderiv>`, `<simplex>`, `<simplex,suffderiv>`, `<suffderiv>`
3. META (?): `<nativ>`, `<frei>`, etc., but also  `<NGeo-aner-NMasc_s_0>`, `<NGeo-anisch-Adj+>` which include constrains on base and the result (are these identifiers for certain rule groups?), can also be multiple values, e.g. `<frei,fremd,gebunden,lang>`
4. RULE_TYPE: `<deriv>`, `<kompos>` (not clear what the latter involves, seems to be primarily applied for foreign language compounds, e.g., "-krat" in "Technokrat", originally a Greek compound, but a transparent suffix to German native speakers, hence "Bürokrat" which is *not* a Greek compound, but just follows the Greek pattern)
5. BASE_POS: note that these can be part of speech *groups*: `<ABK,ADJ,NE,NN>`, `<ABK,ADJ,NE,NN,V>`, `<ABK,NE,NN>`, `<ABK,NN>`, `<ADJ>`, `<ADJ,CARD>`, `<ADJ,CARD,NN,V>`, `<ADJ,NE,NN>`, `<ADJ,NN>`, `<ADJ,NN,V>`, `<ADV,NE,NN,V>`, `<CARD>`, `<CARD,DIGCARD,NE>`, `<CARD,NN>`, `<DIGCARD>`, `<NE>`, `<NE,NN>`, `<NE,NN,V>`, `<NN>`, `<NN,V>`, `<ORD>`, `<V>`
6. FORM: `er`, `ig`, etc.
7. RESULT_POS: `<NN>`, `<ADJ>`, `<V>`, `<ADV>`, `<NE>`
8. MORPH_TYPE: "`<SUFF>`"
9. BASE_TYPE (?): `<base>`, `<kompos>` or `<deriv>` (cannot be about the result because it includes `<base>`)
  Not clear how this is related to colum 4. In fact, they seem to be independent from each other as all combinations occur:

    155 <deriv>	<base>
    65 <deriv>	<deriv>
    103 <deriv>	<kompos>
    29 <kompos>	<base>
    25 <kompos>	<deriv>
    28 <kompos>	<kompos>

10. RESULT_META (?): `<frei>`, `<fremd>`, `<gebunden>`, `<kurz>`, `<lang>`, `<nativ>` (why do we have that twice? maybe just to propagate the META feature?). Note that these features do not have to overlap with those in column 3, e.g.,

    <Suff_Stems>	<prefderiv,simplex,suffderiv>	<frei,fremd,gebunden,lang>	<deriv>	<ADJ,NN,V>	isch	<ADJ>	<SUFF>	<base>	<nativ>	<Adj+>
    <Suff_Stems>	<prefderiv,simplex,suffderiv>	<frei,fremd,gebunden,lang>	<deriv>	<ADJ,NN,V>	isch	<ADJ>	<SUFF>	<kompos>	<nativ>

11. RESULT_FEATS (optional): paradigm information about the derived word (may be an identifier for a paradigm or inflection type)
   values: ADJ: `<Adj+>`, `<Adj0>`; NN: `<NMasc_s_0>`, `<NNeut_s_0>`; V: `<VVReg-el/er>`

### Kompos_Stems

Apparently, this is for stems that cannot occur in isolation (but some have the `<frei>` tag in META).

1. ENTRY_TYPE: `<Kompos_Stems>`
2. FORM: e.g., `Erst`
3. POS: `<ADJ>`, `<ADV>`, `<NE>`, `<NN>`, `<ORD>`, `<OTHER>`, `<V>`
4. RULE_TYPE: `<kompos>`
5. META: `<frei>` ("Pharma"), `<gebunden>` ("anti"), `<nativ>`, `<fremd>` ("Mini"), `<klassisch>` ("Mega", "Micro", "Pseudo")

No FEATS column because these do never occur in isolation. Not sure I understand the difference between `<fremd>` and `<klassisch>`. I guess the latter is primarily for words of Latin and Greek origin, the former for modern loan words (but even though "Mini" may have come through English, it is Latin in origin)

### Other entry types

If the first column contains a different tag, this is something like a modifier that adds information. The *next* column then contains the actual ENTRY_TYPE (or another modifier, if multiple apply).

- Initial

  1. ENTRY_TYPE: "`<Initial>`"
  2. SUB_TYPE: "`<BaseStems>`", "`<Kompos_Stems>`"
  3. continues like entries of SUB_TYPE

- ge

  1. ENTRY_TYPE: "`<ge>`"
  2. SUB_TYPE: "`<Base_Stems>`"
  3. continues like SUB_TYPE

- NoDef

  1. ENTRY_TYPE: "`<NoDef>`"
  2. SUB_TYPE: "`<Initial>`", "`<BaseStems>`"
  3. continues like entries of SUB_TYPE

- QUANT

  1. ENTRY_TYPE: "`<QUANT>`"
  2. SUB_TYPE: "`<Suff_Stems>`"
  3. continues like SUB_TYPE

- <NoHy>

  1. ENTRY_TYPE: `<NoHy>`
  2. SUB_TYPE: `<Base_Stems>`
  3. continues like SUB_TYPE

## Form notation

Aside from plain strings (`[a-zA-Z\-\.]`), the following reserved characters occur:

`/` this seems indicate an alternative lexicalization of the full word (global scope), e.g., in the following expression

	 <Base_Stems>	und/o:ud:ne:dr:<>/oder	<OTHER>	<base>	<nativ>	<Konj-Kon>

   The three options indicated are `und`, `oder` and an expression that is actually a merger of both: `[ou][dn][ed][r]?`

`:` this seems to indicate an alternative character (local scope) between two elements.
    However, this is order-sensitive. If multiple characters alternate, then the first argument of `:` will continue the first alternative, the second will continue the first.

    examples:
    - `o:ud:ne:dr:<>` => `oder` [first arguments of `:`], `und` [second arguments of `:`, empty strings removed]
    - `mü:us:ßs:<>e:<>n:<>` => `müssen` [first arguments], `muß` [second arguments of `:`, empty strings removed]

    As the examples show, these mergers are automatically generated and do not necessarily represent morphophonological processes (they could be used for that, though).
    For the conversion, we can just compile them out.

`<>` empty string, occurs only in alternations, but can also represent zero morphs, e.g.,

    <Suff_Stems>	<simplex>	<nativ>	<deriv>	<CARD>	<>	<NN>	<SUFF>	<base>	<nativ>	<NFem_0_en>

Note that these forms provide no information about disambigutation, the morphology is thus primary intended for parsing, not for generation. (It would overgenerate for any case of stem alternation.)
