# Handoff channel

Two agents work on the Year Seventeen selector and stay in separate trees. This
directory is the only place they exchange anything.

    handoff/inbox/     <- Codex writes here.  Claude Code reads.
    handoff/outbox/    <- Claude Code writes here.  Codex reads.
    handoff/archive/   <- handled messages move here, nothing is deleted.

## Convention

One message per file. Markdown. Name it so order and author are obvious:

    NNN-from-codex-short-subject.md
    NNN-from-claude-short-subject.md

Start every message with these four lines, then the body:

    From:    codex | claude-code
    Date:    YYYY-MM-DD HH:MM
    Subject: one line
    Replies-to: filename, or "none"

Write the whole message before it lands in the directory. A watcher fires on
the file appearing, so a half-written file will be read half-written. Write to a
temp name in the same directory and rename it into place.

## Who owns what

| | Claude Code | Codex |
|---|---|---|
| Writes to | `~/timeline` | the Polish project |
| Reads | both | both |

Claude Code does not write into `~/Documents/ChatGPT/Polish`. If it produces
something that belongs there, it goes in `outbox/` and Codex places it.

## Status

Claude Code is watching `inbox/` and will be woken when a file appears.
Its session address is `timeline-47`, though that channel does not reach Codex.
This directory does.
