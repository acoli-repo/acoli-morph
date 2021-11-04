# Linking

This is for generating (shallow and heuristic) links across different datasets so that they can be queried in conjunction with each other.

Link and test using

    $> make

## Known issues

- For some morphemes, the linking algorithm overgenerates and produces links without matches. This may be an issue with blank nodes.
- For language identification, UniMorph uses ISO639-3 tags and the others use BCP47 tags. For German, we just match the first two characters, for other languages, this heuristic is either not applicable (Spanish: `spa` vs. `es`) or produces incorrect results (`rom` Romani vs. `ro` Romanian).
