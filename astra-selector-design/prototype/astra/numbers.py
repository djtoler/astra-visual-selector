"""Spoken-number normalization.

The narration says "ninety-seven percent" and the transcript says "97 %".
This documentary is built on figures, so phrase matching has to see those as
the same token sequence.
"""
import re

UNITS = {"zero":0,"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,
         "eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,
         "fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,
         "nineteen":19}
TENS  = {"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,
         "eighty":80,"ninety":90}
SCALE = {"hundred":100,"thousand":1000,"million":1_000_000,"billion":1_000_000_000}
KEEP_SCALE = {"million","billion","thousand"}   # spoken aloud, keep as a word


def _chunk_value(toks):
    """Value of a run of number words, or None."""
    total, current, seen = 0, 0, False
    for t in toks:
        if t in UNITS:
            current += UNITS[t]; seen = True
        elif t in TENS:
            current += TENS[t]; seen = True
        elif t == "hundred":
            current = (current or 1) * 100; seen = True
        else:
            return None
    if not seen:
        return None
    return total + current


def normalize(text):
    """Rewrite spoken numbers as digits, leaving magnitude words in place."""
    text = str(text).lower()
    text = text.replace("percent", "%").replace("per cent", "%")
    # hyphenated compounds first: twenty-eight -> twenty eight
    text = re.sub(r"(?<=[a-z])-(?=[a-z])", " ", text)
    toks = text.split()

    out, i = [], 0
    while i < len(toks):
        raw = toks[i]
        word = re.sub(r"[^\w%.]", "", raw)
        if word in UNITS or word in TENS or word == "hundred":
            j = i
            run = []
            while j < len(toks):
                w = re.sub(r"[^\w%.]", "", toks[j])
                if w in UNITS or w in TENS or w == "hundred":
                    run.append(w); j += 1
                else:
                    break
            val = _chunk_value(run)
            if val is None:
                out.append(raw); i += 1
                continue
            # "four point four" -> 4.4
            if j + 1 < len(toks) and re.sub(r"[^\w]", "", toks[j]) == "point":
                nxt = re.sub(r"[^\w]", "", toks[j + 1])
                if nxt in UNITS:
                    val = float(f"{val}.{UNITS[nxt]}")
                    j += 2
            out.append(str(val))
            i = j
        else:
            out.append(raw); i += 1
    return " ".join(out)
