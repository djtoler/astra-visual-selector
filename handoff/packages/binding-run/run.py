#!/usr/bin/env python3
"""Wire the beat and judgment prompts to Sonnet 5 through the authenticated CLI."""
import json, re, subprocess, sys, pathlib
P = pathlib.Path(__file__).resolve().parent
PROMPTS = P.parent / "prompts"
MODEL = "claude-sonnet-5"

ENV = pathlib.Path("/Users/dwaynetoler/timeline/.env")
USAGE = {"calls":0, "in":0, "out":0}

def _key():
    for ln in ENV.read_text().splitlines():
        # the .env spells it ANTROPIC_API_KEY; accept either
        if ln.split("=")[0].strip() in ("ANTHROPIC_API_KEY","ANTROPIC_API_KEY"):
            return ln.split("=",1)[1].strip().strip('"').strip("'")
    raise RuntimeError("no API key in .env")

def ask(prompt, timeout=300, max_tokens=8000):
    """Anthropic Messages API. Bills the API key, not the subscription."""
    import urllib.request, urllib.error
    body = json.dumps({"model": MODEL, "max_tokens": max_tokens,
                       "messages":[{"role":"user","content":prompt}]}).encode()
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=body,
        headers={"x-api-key": _key(), "anthropic-version":"2023-06-01",
                 "content-type":"application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.loads(r.read())
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"model call failed HTTP {e.code}: {e.read()[:300].decode()}")
    u = d.get("usage", {})
    USAGE["calls"] += 1
    USAGE["in"]  += u.get("input_tokens", 0)
    USAGE["out"] += u.get("output_tokens", 0)
    return "".join(b.get("text","") for b in d.get("content", []))

def spend(price_in=3.0, price_out=15.0):
    """Sonnet 5 rates. Returns dollars actually billed so far this process."""
    return USAGE["in"]/1e6*price_in + USAGE["out"]/1e6*price_out

def as_json(text):
    m = re.search(r'```(?:json)?\s*(.*?)```', text, re.S)
    body = m.group(1) if m else text
    s, e = body.find('{'), body.rfind('}')
    if s < 0 or e < 0: raise ValueError(f"no JSON in reply: {text[:200]}")
    return json.loads(body[s:e+1])

def fill(tmpl, **kw):
    for k, v in kw.items():
        tmpl = tmpl.replace("{"+k+"}", str(v))
    return tmpl

def beats(passage, before="", after=""):
    t = (P/"PROMPT-beats.md").read_text()
    return as_json(ask(fill(t, passage=passage, before=before, after=after)))["beats"]

def judge(beat, cand, lo, hi):
    t = PROMPTS/"PROMPT-judge-single.md".read_text()
    t = t.split("---",1)[1] if "---" in t else t
    return as_json(ask(fill(t,
        quote=beat.get("quote",""), takeaway=beat.get("takeaway",""),
        must_be_true="; ".join(beat.get("must_be_true") or []) or "none recorded",
        would_be_a_lie="; ".join(beat.get("would_be_a_lie") or []) or "none recorded",
        n=beat.get("entity_count",0), entity_kind=beat.get("entity_kind",""),
        id=cand["id"], description=cand.get("description") or "",
        appropriate_narration="; ".join(cand.get("narration") or []) or "not recorded",
        avoid_when="; ".join(cand.get("avoid") or []) or "not recorded",
        caveats="; ".join(cand.get("caveats") or []) or "not recorded",
        encoding=cand.get("encoding") or "not recorded",
        axes=", ".join(f"{k}={v}" for k,v in (cand.get("axes") or {}).items()) or "unknown",
        lo=lo, hi=hi)))

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv)>1 else "beats"
    if mode == "beats":
        data = json.loads(sys.stdin.read())
        out = beats(data["passage"], data.get("before",""), data.get("after",""))
        print(json.dumps({"beats":out}, indent=1))
