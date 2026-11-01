"""Download the Bavli tractates that claims.json cites from the public Sefaria export on GCS.

Files: data/sefaria/<Tractate>_he.json (William Davidson Aramaic) and _en.json (William Davidson English),
from gs://sefaria-export/json/Talmud/Bavli/<Seder>/<Tractate>/. Needs the gcloud CLI; the bucket is public,
so no sign-in is used. Already downloaded files are skipped; pass --force to download again.
"""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent
OUT = ROOT / "data" / "sefaria"
BUCKET = "gs://sefaria-export"

SEDER = {
    "Zeraim": ["Berakhot"],
    "Moed": ["Shabbat", "Eruvin", "Pesachim", "Shekalim", "Yoma", "Sukkah", "Beitzah", "Rosh Hashanah",
             "Taanit", "Megillah", "Moed Katan", "Chagigah"],
    "Nashim": ["Yevamot", "Ketubot", "Nedarim", "Nazir", "Sotah", "Gittin", "Kiddushin"],
    "Nezikin": ["Bava Kamma", "Bava Metzia", "Bava Batra", "Sanhedrin", "Makkot", "Shevuot", "Avodah Zarah",
                "Horayot"],
    "Kodashim": ["Zevachim", "Menachot", "Chullin", "Bekhorot", "Arakhin", "Temurah", "Keritot", "Meilah",
                 "Tamid"],
    "Tahorot": ["Niddah"],
}
SEDER_OF = {t: s for s, ts in SEDER.items() for t in ts}
FILES = {"he": "Hebrew/William Davidson Edition - Aramaic.json", "en": "English/William Davidson Edition - English.json"}

env = dict(os.environ, CLOUDSDK_AUTH_DISABLE_CREDENTIALS="true")
claims = json.loads((ROOT / "claims.json").read_text(encoding="utf-8"))
tractates = sorted({re.match(r"(.+) \d+[ab]:", c["ref"]).group(1) for c in claims})
OUT.mkdir(parents=True, exist_ok=True)
for i, t in enumerate(tractates, 1):
    for lang, path in FILES.items():
        dest = OUT / f"{t}_{lang}.json"
        if dest.exists() and "--force" not in sys.argv:
            print(f"{i}/{len(tractates)} {t} {lang}: cached", flush=True)
            continue
        src = f"{BUCKET}/json/Talmud/Bavli/Seder {SEDER_OF[t]}/{t}/{path}"
        subprocess.run(["gcloud", "storage", "cp", src, str(dest), "-q"], env=env, check=True, shell=os.name == "nt")
        print(f"{i}/{len(tractates)} {t} {lang}: downloaded", flush=True)
date = subprocess.run(["gcloud", "storage", "cat", f"{BUCKET}/last_export.txt"], env=env, check=True,
                      capture_output=True, text=True, shell=os.name == "nt").stdout[:10]
(ROOT / "data" / "sefaria_export_date.txt").write_text(date + "\n", encoding="utf-8")
print("export date:", date)
