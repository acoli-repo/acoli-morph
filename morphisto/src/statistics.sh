#!/bin/sh

if [ $# -lt 2 ]
then
	echo "Aufruf durch: sh statisics.sh <Automat mit SFST-Automat mit kompaktem Format> <Test-Korpus>" 
	exit 1
fi

echo Frequenzen der verschiedenen Flexionsklassen in MORPHISTO
cat lexicon | grep -o "<[A-Za-z0-9\$\_\-\/\~\(\)\+\?]\+>$" | sort | uniq -c | sort -r -n

echo Frequenzen der Wortarten in MORPHISTO
cat lexicon | grep -E -o "<(V|NN|OTHER|ADJ|ADV|PREF|CARD)>" | sort | uniq -c | sort -r -n       

echo Frequenzen der Stammtypen
cat lexicon | grep -E -o "<(Base_Stems|Kompos_Stems|Deriv_Stems|Pref_Stems)>" | sort | uniq -c | sort -r -n

echo Lasse Test-Korpus "$2" durch den ausgewählten Automaten laufen

#thanks to the people from the University of Zurich for the feedback 
#and the contribution of the following code improvement:


TOKEN=$(wc -l < "$2")
TYPES=$(sort "$2" | uniq | wc -l)

echo "Zeitaufwand:"

TMPFILE=$(mktemp ${TMPDIR:-/tmp}/morphistoXXXXX)
# Hässlich, aber strikt nach POSIX nicht anders möglich. Mit ksh oder
# bash kann man stattdessen folgendes verwenden:
# time fst-infl2 "$1" "$2" 2> /dev/null > "$TMPFILE"
time sh -c "fst-infl2 '$1' '$2' 2> /dev/null > '$TMPFILE'"

# Anzahl rückgabezeilen
RESULT=$(wc -l < $TMPFILE)
# Anzahl zeilen mit "no result for"
NORESULTS=$(grep -c "no result for" $TMPFILE)
# Anzahl analysierte token
WORDFORMS=$((TOKEN - NORESULTS))
# Anzahl zeilen, die eine analyse enthalten
ANALYSE=$((RESULT - TOKEN - NORESULTS))

RATEPOS=$(echo "scale=5; $WORDFORMS/$TOKEN*100" | bc)
RATENEG=$(echo "scale=5; $NORESULTS/$TOKEN*100" | bc)
RATEAN=$(echo "scale=5; $ANALYSE / $WORDFORMS" | bc)

echo Testkorpus "$2"
echo -------------------------------------------------------------------------------
echo Wortformen:                 $TOKEN
echo Davon analysiert:           $WORDFORMS = $RATEPOS %
echo Produzierte Analysen:       $ANALYSE
echo Analysen je Wortform:       $RATEAN
echo Unanalysierbare Wortformen: $NORESULTS = $RATENEG %

rm -f "$TMPFILE"



#TOKEN=`wc -l < $2`
#TYPES=`sort $2 | uniq | wc -l`
#echo Zeitaufwand:
#TMPFILE=`mktemp`
#time fst-infl2 $1 $2 2>/dev/null > $TMPFILE
#NORESULTS=`cat $TMPFILE | grep "no result for " | sort | uniq | wc -l`
#WORDFORMS=`cat $TMPFILE | sed /"no result for\|> "/d | wc -l`
#RATEPOS=`python -c "print float($TOKEN-$NORESULTS)/$TOKEN*100"`
#RATENEG=`python -c "print float($NORESULTS)/$TOKEN*100"`
#echo Testkorpus "$2"
#echo --------------------------------
#echo Wortformen: $TOKEN
#echo Davon analysiert: $RATEPOS %
#echo Produzierte Analysen: $WORDFORMS
#echo Unanalysierbare Wortformen: $NORESULTS = $RATENEG %
