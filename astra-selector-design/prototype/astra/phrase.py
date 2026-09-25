"""Resolve a spoken trigger phrase to a measured timestamp.

The whisper alignment mangles proper nouns ("Absoles" for Ab-Soul, "Lotto" for
Latto), so matching is fuzzy at the token level rather than exact.
"""
import re, difflib
from . import data
from .numbers import normalize

_PUNCT = re.compile(r"[^\w%$]+")


def _norm(tok):
    return _PUNCT.sub("", str(tok).lower())


def _tokens(text):
    return [t for t in (_norm(x) for x in normalize(text).split()) if t]


def window(start, end, pad=0.75):
    """Word records whose span overlaps [start-pad, end+pad]."""
    out = []
    for w in data.words():
        s, e = w.get("start"), w.get("end")
        if s is None or e is None:
            continue
        if e >= start - pad and s <= end + pad:
            out.append(w)
    return out


def resolve(phrase, start, end, min_ratio=0.62):
    """Find `phrase` inside the passage window.

    Returns {found, startSeconds, endSeconds, ratio, matchedText} where
    startSeconds is when the phrase begins being spoken.
    """
    want = _tokens(phrase)
    if not want:
        return {"found": False, "reason": "empty phrase"}
    win = window(start, end)
    if not win:
        return {"found": False, "reason": "no aligned words in window"}
    norm = [_norm(t) for t in normalize(" ".join(w["word"] for w in win)).split()]
    # normalize can merge/split tokens; rebuild a parallel time index
    if len(norm) != len(win):
        norm = [_norm(normalize(w["word"])) for w in win]
    norm = [n for n in norm]

    best = None
    # allow the matched span to be a little shorter or longer than the query
    for span in range(max(1, len(want) - 2), len(want) + 3):
        for i in range(0, max(1, len(norm) - span + 1)):
            cand = norm[i:i + span]
            if not cand:
                continue
            ratio = difflib.SequenceMatcher(None, " ".join(want), " ".join(cand)).ratio()
            if best is None or ratio > best["ratio"]:
                best = {"ratio": ratio, "i": i, "span": span,
                        "startSeconds": round(win[i]["start"], 2),
                        "endSeconds": round(win[i + len(cand) - 1]["end"], 2),
                        "matchedText": " ".join(w["word"] for w in win[i:i + len(cand)]).strip()}
    if best and best["ratio"] >= min_ratio:
        return {"found": True, "startSeconds": best["startSeconds"],
                "endSeconds": best["endSeconds"], "ratio": round(best["ratio"], 3),
                "matchedText": best["matchedText"]}
    return {"found": False, "reason": "no match above threshold",
            "bestRatio": round(best["ratio"], 3) if best else None,
            "bestText": best.get("matchedText") if best else None}


def transcript(start, end):
    return " ".join(w["word"] for w in window(start, end, pad=0)).strip()
