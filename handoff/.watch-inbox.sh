#!/bin/zsh
# Waits for a new message in handoff/inbox, prints it, exits.
H=/Users/dwaynetoler/timeline/handoff
while :; do
  f=$(ls -1 "$H/inbox" 2>/dev/null | head -1)
  if [ -n "$f" ]; then
    echo "NEW INBOX MESSAGE:"
    echo "== $f"
    cat "$H/inbox/$f"
    exit 0
  fi
  sleep 60
done
