"""Search a tractate in the Sefaria export: grep_daf.py <Tractate> <regex> [daf-from daf-to]."""
import json, re, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
SEF = Path(__file__).parent / "data" / "sefaria"
t, pat = sys.argv[1], sys.argv[2]
he = json.loads((SEF / f"{t}_he.json").read_text(encoding="utf-8"))["text"]
en = json.loads((SEF / f"{t}_en.json").read_text(encoding="utf-8"))["text"]
full = "--full" in sys.argv
for i, amud in enumerate(he):
    for j, seg in enumerate(amud):
        s = re.sub(r"<[^>]+>", "", seg)
        if re.search(pat, s):
            daf = f"{i // 2 + 1}{'ab'[i % 2]}"
            print(f"{t} {daf}:{j+1} | {s if full else s[:200]}")
            if full: print("   EN:", re.sub(r"<[^>]+>", "", en[i][j]))
