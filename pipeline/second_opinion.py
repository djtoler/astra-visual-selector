#!/usr/bin/env python3
"""Send a decision to Codex for a second opinion, over the handoff channel.

  second_opinion.py <decision.md> [context-file ...]

Writes a numbered message into handoff/inbox. Codex replies into handoff/outbox when it
next runs; there is no codex CLI here, so this is asynchronous.
"""
import sys, pathlib, datetime, re, shutil
H = pathlib.Path("/Users/dwaynetoler/timeline/handoff")

def next_number():
    used = []
    for d in ("inbox", "outbox", "archive"):
        for f in (H / d).glob("*.md"):
            m = re.match(r"(\d{3})-", f.name)
            if m: used.append(int(m.group(1)))
    return max(used, default=0) + 1

def main(decision_path, context_paths):
    n = next_number()
    dec = pathlib.Path(decision_path).read_text()
    parts = [
        f"From:    claude-code",
        f"Date:    {datetime.datetime.now():%Y-%m-%d %H:%M}",
        f"Subject: Second opinion requested by the user on an operational decision",
        "",
        "The user asked for your opinion on the decision below before he decides. He is CEO",
        "and makes the call; we both advise. Please reply with your recommendation and your",
        "reasoning, and say plainly where you disagree with mine.",
        "",
        "---",
        "",
        dec.strip(),
        "",
    ]
    for c in context_paths:
        p = pathlib.Path(c)
        if not p.exists():
            parts += [f"## Context: {p.name} — NOT FOUND", ""]
            continue
        body = p.read_text()
        clip = body if len(body) < 12000 else body[:12000] + "\n...[truncated]"
        parts += [f"## Context: {p.name}", "", "```", clip.strip(), "```", ""]
    out = H / "inbox" / f"{n:03d}-from-claude-second-opinion.md"
    tmp = out.with_suffix(".tmp")
    tmp.write_text("\n".join(parts))
    tmp.rename(out)
    print(f"sent: {out.name}  ({len(chr(10).join(parts))} chars, {len(context_paths)} context file(s))")
    print("Codex replies into handoff/outbox when it next runs. No CLI, so this is async.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__); sys.exit(1)
    main(sys.argv[1], sys.argv[2:])
