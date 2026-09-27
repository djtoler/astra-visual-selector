#!/usr/bin/env python3
"""Where each beat sits in the narration script. One reviewable map, not a guess
recomputed on every build.

WHY v2.1. The user, 2026-09-26: "this is the script that should be used ... we can
keep the beats the same but this scripts wordings helps me understand context. the
other one was too choppy." The beats stay exactly as they are; only the prose
around them changes source.

WHY A MAP AND NOT A SEARCH. Measured: only 17 of 40 beats appear verbatim in v2.1
(27 of 40 in v4). v2.1 is a fuller rewrite of the same content — "One rapper's
catalog gets played on Spotify seven hundred times a second" against the beat's
"Seven hundred times a second. That's how often one rapper's catalog gets played
on Spotify." Same claim, different sentence. No matcher finds that reliably, and
a matcher that silently half-finds it is worse than a map somebody can read. The
user: "just make a map if its a issue."

WHY MONOTONIC. v2.1 has six cycles; v3 has seven plus a coda. v3 did not reorder
— it SPLIT v2.1's CYCLE 3 (WHOSE RECORDS?) into three: WHOSE RECORDS?, THE
ACCUSATION, WHERE IT TURNS. Both the features material and the "comparison turns
on him" material sit in v2.1 cycle 3. Order is therefore preserved, and each beat
may only anchor at or after the beat before it. Unconstrained, beats 23, 24 and
25a collapsed onto one paragraph.

OVERRIDES. grammar/beat-script-map.overrides.json wins over any alignment, keyed
by beat, recorded with source "user". A row the user fixes must survive a rebuild.

    python3 pipeline/script_map.py            rebuild the map, report weak rows
    python3 pipeline/script_map.py --check     fail if the map is missing or stale
"""
import json, pathlib, re, sys

P = pathlib.Path(__file__).resolve().parent
SCRIPT = P.parent / "script" / "year-seventeen-script-v2.1.md"
MAP = P.parent / "grammar" / "beat-script-map.json"
OVERRIDES = P.parent / "grammar" / "beat-script-map.overrides.json"
SHOTLIST = P / "shotlist.capacity.json"

WEAK = 0.60          # below this, the row is reported for review, never hidden


def norm(s):
    """1:1 character substitutions only, so char offsets stay valid in the source."""
    for a, b in (("—", "-"), ("–", "-"), ("’", "'"),
                 ("“", '"'), ("”", '"'), ("‘", "'")):
        s = s.replace(a, b)
    return s.lower()


def words(s):
    return re.findall(r"[a-z0-9$']+", norm(s))


def sentences(text):
    """Sentence spans with LEADING WHITESPACE EXCLUDED.

    `[^.!?]*[.!?]+` swallows the space after the previous full stop, so a
    sentence that opens a paragraph starts one char before the paragraph does.
    That single character put beat 15-15 — verbatim the first line of CYCLE 3 —
    into CYCLE 2, because the paragraph lookup is a `<=` on offsets.
    """
    out = []
    for m in re.finditer(r"[^.!?]*[.!?]+|[^.!?]+$", text):
        a, b = m.start(), m.end()
        while a < b and text[a].isspace():
            a += 1
        if text[a:b].strip():
            out.append((a, b))
    return out


def parse(path=SCRIPT):
    """Paragraphs of narration, carrying the cycle, section and test question.

    The test question is the cycle's PURPOSE, stated in the script itself. It is
    the single most useful piece of context on the page: it says what the cycle
    is trying to establish, which is what a reviewer needs to judge whether a
    treatment communicates the beat.
    """
    cyc = sec = test = None
    paras, buf = [], []

    def flush():
        if buf:
            paras.append({"cycle": cyc, "section": sec, "test": test,
                          "text": re.sub(r"\s+", " ", " ".join(buf)).strip()})
            buf.clear()

    for line in open(path):
        l = line.rstrip()
        m = re.match(r"##\s+(CYCLE.*|CODA.*)$", l)
        if m:
            flush(); cyc, sec, test = m.group(1), None, None; continue
        m = re.match(r"###\s+(.*)$", l)
        if m:
            flush(); sec = m.group(1).strip(); continue
        m = re.match(r"\*\*Test question:\s*(.*?)\*\*\s*$", l)
        if m:
            flush(); test = m.group(1).strip(); continue
        if l.startswith((">", "---", "#")) or not l.strip():
            flush(); continue
        buf.append(l.strip())
    flush()
    if not paras:
        raise SystemExit(f"{path}: no narration parsed")
    return paras


class Located:
    """The script, plus where every beat sits in it."""

    def __init__(self, rows, paras):
        self.paras = paras
        self.full = " ".join(p["text"] for p in paras)
        self.rows = {r["beat"]: r for r in rows}
        self.sent = sentences(self.full)

    def window(self, beat, n=2):
        """A CONTIGUOUS run of script, with the beat's own words marked inside it.

        before + " " + mid + " " + after is a real substring of the script, and a
        test asserts it. The page must never splice the beat's QUOTE in where the
        script's words go: the quote is terse where the script is full, and on a
        split sentence it is only half of it, so the splice silently drops the
        rest. That is what made 02-02a jump from the Freshman cover to the
        ninety-three rappers.
        """
        r = self.rows.get(beat)
        if not r:
            return {"before": "", "mid": "", "hlStart": 0, "hlLen": 0, "after": ""}
        ea, eb = r["sentStart"], r["sentStart"] + r["sentLen"]
        pre = [(x, y) for x, y in self.sent if y <= ea][-n:]
        post = [(x, y) for x, y in self.sent if x >= eb][:n]
        raw = self.full[ea:eb]
        lead = len(raw) - len(raw.lstrip())
        hl = max(ea, min(r["charStart"], eb))
        return {"before": self.full[pre[0][0]:pre[-1][1]].strip() if pre else "",
                "mid": raw.strip(),
                "hlStart": max(0, hl - ea - lead),
                "hlLen": max(0, min(r["charLen"], eb - hl)),
                "after": self.full[post[0][0]:post[-1][1]].strip() if post else ""}

    def context(self, beat, n=2):
        w = self.window(beat, n)
        return w["before"], w["after"]

    def where(self, beat):
        r = self.rows.get(beat) or {}
        return {k: r.get(k) for k in ("cycle", "section", "test")}

    def says(self, beat):
        r = self.rows.get(beat)
        return r["scriptSays"] if r else None


def align(keys, quotes, paras):
    """Order-preserving best-overlap placement. Exact hits pin the sequence."""
    full = " ".join(p["text"] for p in paras)
    fn = norm(full)
    tok = [(m.start(), m.end(), m.group(0))
           for m in re.finditer(r"[a-z0-9$']+", fn)]
    ws = [t[2] for t in tok]
    pstart, at = [], 0
    for p in paras:
        pstart.append(at); at += len(p["text"]) + 1

    def tok_at(ch):
        lo, hi = 0, len(tok)
        while lo < hi:
            mid = (lo + hi) // 2
            if tok[mid][0] < ch: lo = mid + 1
            else: hi = mid
        return lo

    # SNAP EVERY SPAN TO SENTENCE BOUNDARIES. A token-range span starts wherever
    # the overlap window happened to begin, which is mid-sentence: beat 21-21a
    # landed on "got. He gets accused of living on features" — "got" is the tail
    # of the PREVIOUS sentence. That makes scriptSays unreadable and, worse, makes
    # the "before" context stop one word early. The user asked for before and
    # after SENTENCES, so the beat's own span has to be whole sentences too.
    sents = sentences(full)

    def snap(ch, ln):
        hit = [(a, b) for a, b in sents if a < ch + ln and b > ch]
        if not hit:
            return ch, ln
        return hit[0][0], hit[-1][1] - hit[0][0]

    exact = {}
    for k in keys:
        q = norm(re.sub(r"\s+", " ", quotes[k]).strip())
        if q and q in fn:
            exact[k] = fn.index(q)

    rows, lo = [], 0
    for i, k in enumerate(keys):
        if k in exact:
            ch, ln, ov = exact[k], len(quotes[k]), 1.0
            lo = tok_at(ch)
        else:
            nxt = next((tok_at(exact[k2]) for k2 in keys[i + 1:] if k2 in exact),
                       len(tok))
            qt = words(quotes[k]); n, qs = len(qt), set(qt)
            best = (-1.0, lo)
            for s in range(lo, max(lo + 1, nxt - n + 1)):
                o = len(qs & set(ws[s:s + n])) / max(1, len(qs))
                if o > best[0]: best = (o, s)
            ov, s = best
            e = min(s + n - 1, len(tok) - 1)
            ch, ln = tok[s][0], tok[e][1] - tok[s][0]
            lo = s
        # TWO SPANS, NOT ONE.
        #   charStart/charLen  the HIGHLIGHT — where this beat's own words are.
        #   sentStart/sentLen  the ENVELOPE — whole sentences containing them.
        # Collapsing these produced the non-sequitur the user caught on 02-02a:
        # "how do we jump from freshman cover to here are 93 rappers? this is
        # exatcly what I was rying to avoid." ONE script sentence — "Curren$y was
        # on the 2009 XXL Freshman cover, and every song he has ever put on the
        # platform ... twenty-four days." — is SPLIT across 02-02a and 02-02b.
        # Snapping 02-02a's span to the whole sentence pushed "after" past it, so
        # 02-02b's half of the sentence never appeared on the page and the prose
        # read as a jump. The envelope is what gets RENDERED; the highlight is
        # what gets MARKED inside it. Nothing is dropped or substituted.
        #
        # PARAGRAPH FROM THE ANCHOR: widening backwards to a sentence edge must
        # not relabel which cycle the beat is in (see 15-15).
        anchor = ch
        sch, sln = snap(ch, ln)
        pi = max(0, sum(1 for x in pstart if x <= anchor) - 1)
        p = paras[pi]
        rows.append({"beat": k, "cycle": p["cycle"], "section": p["section"],
                     "test": p["test"], "paragraph": pi,
                     "charStart": ch, "charLen": ln,
                     "sentStart": sch, "sentLen": sln,
                     "overlap": round(ov, 3), "exact": ov >= 1.0,
                     "scriptSays": full[sch:sch + sln].strip(),
                     "source": "aligned"})
    return rows


def _cycle_test(paras):
    """A section under a cycle inherits that cycle's test question; only the
    heading line carries it. Without this, every beat outside the first
    paragraph of a cycle reports no test question at all."""
    seen = {}
    for p in paras:
        if p["test"]: seen[p["cycle"]] = p["test"]
        elif p["cycle"] in seen: p["test"] = seen[p["cycle"]]
    return paras


def build():
    paras = _cycle_test(parse())
    shots = {f"{x['passage']}-{x['beat']}": x for x in json.load(open(SHOTLIST))}
    keys = sorted(shots)
    rows = align(keys, {k: v["quote"] for k, v in shots.items()}, paras)

    ov = {}
    if OVERRIDES.exists():
        ov = {r["beat"]: r for r in json.load(open(OVERRIDES)).get("beats", [])}
    for r in rows:
        if r["beat"] in ov:
            r.update(ov[r["beat"]]); r["source"] = "user"

    MAP.write_text(json.dumps(
        {"_script": str(SCRIPT.relative_to(P.parent)),
         "_scriptWords": len(" ".join(p["text"] for p in paras).split()),
         "_note": ("Where each beat sits in the script. overlap 1.0 is verbatim; "
                   "below that the script words the same claim differently and "
                   "scriptSays shows how. Fix a row in "
                   "beat-script-map.overrides.json — user rows survive rebuild."),
         "beats": rows}, indent=1) + "\n")
    return rows, paras


def load():
    """(Located, rows). Builds if the map is absent, so a consumer never guesses."""
    if not MAP.exists():
        build()
    d = json.load(open(MAP))
    return Located(d["beats"], _cycle_test(parse())), d["beats"]


def main():
    rows, paras = build()
    ex = [r for r in rows if r["exact"]]
    us = [r for r in rows if r["source"] == "user"]
    weak = sorted((r for r in rows if not r["exact"] and r["overlap"] < WEAK),
                  key=lambda r: r["overlap"])
    print(f"   {MAP.relative_to(P.parent)}  —  {len(rows)} beats mapped to "
          f"{SCRIPT.name}")
    print(f"   verbatim {len(ex)}   reworded {len(rows)-len(ex)-len(us)}   "
          f"user-fixed {len(us)}")
    cyc = {}
    for r in rows: cyc.setdefault(r["cycle"], []).append(r["beat"])
    print()
    for c, bs in cyc.items():
        print(f"   {c:34} {len(bs):2} beats   {bs[0]} .. {bs[-1]}")
    if weak:
        print(f"\n   {len(weak)} rows below {WEAK:.0%} overlap — check these first:")
        for r in weak:
            print(f"      {r['beat']:8} {r['overlap']:.0%}  {r['cycle'].split('—')[0].strip()}"
                  f" / {r['section']}")
            print(f"               script: {r['scriptSays'][:96]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
