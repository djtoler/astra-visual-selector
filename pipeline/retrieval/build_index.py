#!/usr/bin/env python3
"""Embed templates and beats LOCALLY and load them into pgvector.

No text leaves the machine. Vectors come from macOS NaturalLanguage via
local_embeddings.swift — the same embedder Codex's RAG pilot used, reused deliberately
so a comparison against that pilot is like for like.

KNOWN LIMITATION, and it decides how any result here must be read: the tokenizer is
[A-Za-z]+, so every DIGIT and all WORD ORDER are discarded. "thirty songs past a
billion" keeps only the words. "one vs many" and "many vs one" are identical vectors.
A negative result from this index is INCONCLUSIVE, not evidence that relevance ranking
fails.

    python3 pipeline/retrieval/build_index.py [--write]
"""
import json, pathlib, subprocess, sys
P = pathlib.Path(__file__).resolve().parent
ROOT = P.parent.parent
sys.path.insert(0, str(ROOT / "match-trial"))
import candidates as C

SWIFT = P / "local_embeddings.swift"
DB = ["docker", "exec", "-i", "contradiction-pgvector",
      "psql", "-U", "contradiction", "-d", "beat_template_retrieval"]
MODEL = "macos-NaturalLanguage-word-en-300d"

def embed(texts):
    """One subprocess for all of them; the model load dominates the cost."""
    r = subprocess.run(["swift", str(SWIFT)], input=json.dumps({"texts": texts}),
                       capture_output=True, text=True)
    if r.returncode: raise RuntimeError(r.stderr[:300])
    d = json.loads(r.stdout)
    return d["vectors"] if isinstance(d, dict) and "vectors" in d else d

def _flat(v):
    return "; ".join(str(x) for x in v) if isinstance(v, list) else ("" if v is None else str(v))

# Text construction copied EXACTLY from Codex's run_embeddings.py, so a comparison with
# their pilot measures the placement of the signal and not a difference in wording.
def template_text(r):
    c = r.get("capability") or {}
    return " ".join([
        f"Visual template: {_flat(r.get('title'))}.",
        f"Scene appearance and movement: {_flat(r.get('description'))}.",
        f"Suitable narration: {_flat(r.get('useWhen'))}. {_flat(r.get('narration'))}.",
        f"Visual encoding: {_flat(r.get('encoding'))}.",
        f"Observed structure: {_flat(c.get('asserts'))}.",
        f"Carries visually: {_flat(c.get('carries'))}.",
        f"Readable on screen: {_flat(c.get('readable'))}.",
        f"Arrangement: {_flat(c.get('structure'))}; staging: {_flat(c.get('staging'))}.",
    ])

def beat_text(b):
    return " ".join([
        f"Visual job: {b['job'].replace('_', ' ')}.",
        f"Narration: {b['quote']}.",
        f"Visual takeaway: {b.get('takeaway')}.",
        f"Must be visually perceptible: {_flat(b.get('must_be_perceptible'))}.",
        f"Must remain true: {_flat(b.get('must_be_true'))}.",
        f"Number of focal entities: {b.get('entity_count')}.",
    ])

def main(argv):
    pool = C.load()
    beats = [b for v in json.load(open(ROOT / "pipeline" / "beats-all.json")).values() for b in v]
    tt = [template_text(r) for r in pool]
    bt = [beat_text(b) for b in beats]
    # ONE call. The Swift computes IDF over whatever it is handed, so embedding the
    # two sets separately gives them different term weights and their cosines are not
    # comparable. Codex's pilot does embed_locally(candidate_texts + query_texts);
    # embedding them apart was a real bug in the first version of this file.
    print(f"embedding {len(tt)} templates and {len(bt)} beats in ONE call "
          f"(shared IDF corpus), locally...")
    allv = embed(tt + bt)
    tv, bv = allv[:len(tt)], allv[len(tt):]
    print(f"   {len(tv)} template vectors, {len(bv)} beat vectors, {len(tv[0])} dims")
    empties = [pool[i]["id"] for i, v in enumerate(tv) if not any(v)]
    if empties: print(f"   WARN {len(empties)} templates embedded to a zero vector: {empties[:4]}")
    if "--write" not in argv:
        print("\nnot written. Re-run with --write to load into pgvector.")
        return 0
    def esc(s): return s.replace("'", "''")
    sql = ["BEGIN;", "TRUNCATE template_vectors;", "TRUNCATE beat_vectors;"]
    for r, t, v in zip(pool, tt, tv):
        sql.append(f"INSERT INTO template_vectors VALUES ('{esc(r['id'])}','{esc(t[:4000])}',"
                   f"'{v}','{MODEL}',{len(v)},now());")
    for b, t, v in zip(beats, bt, bv):
        sql.append(f"INSERT INTO beat_vectors VALUES ('{esc(b['id'])}','{esc(b['job'])}',"
                   f"'{esc(t[:4000])}','{v}','{MODEL}',{len(v)},now());")
    sql.append("COMMIT;")
    r = subprocess.run(DB, input="\n".join(sql), capture_output=True, text=True)
    if r.returncode: print(r.stderr[:400]); return 1
    out = subprocess.run(DB + ["-tc", "select (select count(*) from template_vectors), "
                                      "(select count(*) from beat_vectors);"],
                         capture_output=True, text=True).stdout.strip()
    print(f"\nloaded: {out}")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
