#!/bin/zsh
cd /Users/dwaynetoler/timeline/pipeline
for r in "6 10" "11 15" "16 20" "21 25" "26 30"; do
  set -- ${=r}
  echo "=== passages $1-$2 ==="
  python3 -u extract.py $1 $2 2>&1 | grep -E "^--- passage|^  \[" || echo "  BATCH FAILED"
done
echo "=== EXTRACTION COMPLETE ==="
python3 -c "
import json;d=json.load(open('beats-all.json'))
print('passages:',len(d),' beats:',sum(len(v) for v in d.values()))"
