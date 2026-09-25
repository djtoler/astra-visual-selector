#!/usr/bin/env python3
"""What has already gone wrong with this file, function or idea?

    python3 no-drifting/check.py candidates.py
    python3 no-drifting/check.py shape
    python3 no-drifting/check.py --index

Run BEFORE editing anything that appears in the log. Twenty-five entries were written
on 2026-09-20 alone and several are the same defect recurring, because nothing made the
earlier entry visible at the moment of the repeat.
"""
import pathlib, re, sys
LOG = pathlib.Path(__file__).resolve().parent / "LOG.txt"

def entries():
    raw = LOG.read_text().split("=" * 80)
    out = []
    for block in raw:
        m = re.search(r"^\[(\d{4})\]\s+(\S+)\s+(.+)$", block.strip(), re.M)
        if m: out.append({"n": m.group(1), "date": m.group(2),
                          "title": m.group(3).strip(), "body": block.strip()})
    return out

def main(argv):
    es = entries()
    if len(argv) < 2 or argv[1] in ("--index", "-i"):
        print(f"{len(es)} entries in no-drifting/LOG.txt\n")
        for e in es:
            done = "open" if re.search(r"^STATUS\s+open", e["body"], re.M) else "    "
            print(f"  [{e['n']}] {done}  {e['title'][:86]}")
        openn = [e for e in es if re.search(r"^STATUS\s+open", e["body"], re.M)]
        if openn: print(f"\n{len(openn)} still open: {', '.join(e['n'] for e in openn)}")
        return 0

    q = argv[1].lower()
    hits = [e for e in es if q in e["body"].lower()]
    if not hits:
        print(f"nothing logged for {argv[1]!r} — no prior defect on record.")
        return 0
    print(f"{len(hits)} entr{'y' if len(hits)==1 else 'ies'} mention {argv[1]!r}:\n")
    for e in hits:
        print("=" * 78)
        print(e["body"])
        print()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
