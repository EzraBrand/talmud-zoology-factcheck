"""Build report.md, factcheck.csv and docs/index.html from claims.json + the Sefaria Bavli export.

Each claim's "ref" is "Tractate Daf:seg" or "Tractate Daf:seg1-seg2". The Hebrew (William Davidson
Aramaic) and English (William Davidson) text of those segments is pulled from data/sefaria/.
Citations link to Bekiut, which uses Sefaria's daf and segment numbers
(https://bekiut.com/talmud/Bava_Kamma/16a#22); the text source link goes to Sefaria.
"""
import csv
import html
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
ROOT = Path(__file__).parent
SEF = ROOT / "data" / "sefaria"
EDITION = "https://ezrabrand.github.io/lewysohn-zoologie"
BUILT = date.today().strftime("%d-%b-%Y")

COL_CLAIM = "Talmud claim"
COL_CITE = "Citation (links to Bekiut)"
COL_LEW = "Lewysohn (1858)"
COL_VERDICT = "Verdict based on modern science"


def clean(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", s)).strip()


def parse(ref):
    m = re.match(r"(.+) (\d+)([ab]):(\d+)(?:[–-](\d+))?$", ref)
    tract, daf, side, a, b = m.groups()
    return tract, int(daf), side, int(a), int(b or a)


def bekiut_url(ref):
    tract, daf, side, a, _ = parse(ref)
    return f"https://bekiut.com/talmud/{tract.replace(' ', '_')}/{daf}{side}#{a}"


def sefaria_url(ref):
    tract, daf, side, a, b = parse(ref)
    seg = f"{a}-{b}" if b != a else f"{a}"
    return f"https://www.sefaria.org/{tract.replace(' ', '_')}.{daf}{side}.{seg}?lang=bi"


def text(ref):
    tract, daf, side, a, b = parse(ref)
    i = (daf - 1) * 2 + (side == "b")
    he = json.loads((SEF / f"{tract}_he.json").read_text(encoding="utf-8"))["text"][i]
    en = json.loads((SEF / f"{tract}_en.json").read_text(encoding="utf-8"))["text"][i]
    return " ".join(clean(he[j]) for j in range(a - 1, b)), " ".join(clean(en[j]) for j in range(a - 1, b))


def md_links(s):
    """Markdown [text](url) -> HTML anchor, for the sources list."""
    s = html.escape(s, quote=False)
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)


claims = json.loads((ROOT / "claims.json").read_text(encoding="utf-8"))
sources = json.loads((ROOT / "sources.json").read_text(encoding="utf-8"))
export = (ROOT / "data" / "sefaria_export_date.txt").read_text(encoding="utf-8").strip()
for c in claims:
    c["he"], c["en"] = text(c["ref"])
    c["bekiut"], c["sefaria"] = bekiut_url(c["ref"]), sefaria_url(c["ref"])
    # The reading edition has no § anchors; a text fragment scrolls to the § heading.
    c["lew_url"] = f"{EDITION}/{c['lewysohn_page']}.html#:~:text=%C2%A7.%20{c['lewysohn_par']}."
    c["lew_label"] = f"§ {c['lewysohn_par']}"

TITLE = f"Talmud zoology fact-check: claims 1–{len(claims)}"
INTRO = (f"{len(claims)} zoological assertions of the Babylonian Talmud, chosen from the "
         f"parts of Lewysohn, *Die Zoologie des Talmuds* (1858), that are already in English "
         f"([lewysohn-zoologie](https://github.com/EzraBrand/lewysohn-zoologie): pp. 1–158). Each is checked "
         f"against current zoology, and Lewysohn's own 1858 judgement is checked too.")
TEXTNOTE = (f"Talmud text: Sefaria public export (`gs://sefaria-export`, export of {export}), William Davidson "
            f"edition (Aramaic and English), CC BY-NC. Citations link to Bekiut, which uses the same daf and segment "
            f"numbers. § links go to the English reading edition of Lewysohn. Last built {BUILT}.")

# ---- Markdown ----
md = [f"# {TITLE}", "", INTRO, "", TEXTNOTE, "", "## Summary", "",
      f"| # | {COL_CLAIM} | {COL_CITE} | {COL_LEW} | {COL_VERDICT} |", "|---|---|---|---|---|"]
for c in claims:
    md.append(f"| {c['n']} | {c['topic']} | [{c['ref']}]({c['bekiut']}) | [{c['lew_label']}]({c['lew_url']}): "
              f"{c['lewysohn_short']} | **{c['verdict']}** |")
md += ["", "## Claims", ""]
for c in claims:
    md += [f"### {c['n']}. {c['topic']}", "",
           f"**Citation:** [{c['ref']}]({c['bekiut']}) (Bekiut) · [text on Sefaria]({c['sefaria']})", "",
           f"> {c['he']}", ">", f"> *{c['en']}* (William Davidson translation)", "",
           f"**{COL_CLAIM}:** {c['claim']}", "",
           f"**{COL_LEW}** ([{c['lew_label']}]({c['lew_url']})): {c['lewysohn']}", "",
           f"**Current zoology:** {c['modern']}", "",
           f"**{COL_VERDICT}: {c['verdict']}.** {c['verdict_note']}", ""]
md += ["## Sources for the modern data", ""] + [f"- {s}" for s in sources]
(ROOT / "report.md").write_text("\n".join(md) + "\n", encoding="utf-8")

# ---- CSV ----
rows = [{
    "Generated: #": c["n"],
    f"Generated: {COL_CLAIM} (short)": c["topic"],
    f"Generated: {COL_CLAIM}": c["claim"],
    "Bekiut: Citation": c["ref"],
    "Bekiut: URL": c["bekiut"],
    "Sefaria: URL": c["sefaria"],
    "Sefaria: Hebrew/Aramaic (Davidson)": c["he"],
    "Sefaria: English (Davidson)": c["en"],
    "Lewysohn: §": c["lewysohn_par"],
    "Lewysohn: Reading edition URL": c["lew_url"],
    "Lewysohn: Comment": c["lewysohn"],
    "Lewysohn: Assessment": c["lewysohn_short"],
    "Generated: Current zoology": c["modern"],
    f"Generated: {COL_VERDICT}": c["verdict"],
    "Generated: Verdict note": c["verdict_note"],
} for c in claims]
with open(ROOT / "factcheck.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

# ---- HTML ----
def vclass(v):
    v = v.lower()
    if v.startswith("true") or v.startswith("mostly true"):
        return "t"
    if v.startswith("false") or v.startswith("mostly false"):
        return "f"
    return "p"


e = html.escape
summary_rows = "\n".join(
    f'<tr><td>{c["n"]}</td><td><a href="#c{c["n"]}">{e(c["topic"])}</a></td>'
    f'<td><a href="{e(c["bekiut"])}" target="_blank" rel="noopener">{e(c["ref"])}</a></td>'
    f'<td><a href="{e(c["lew_url"])}" target="_blank" rel="noopener">{e(c["lew_label"])}</a>: {e(c["lewysohn_short"])}</td><td><span class="v {vclass(c["verdict"])}">{e(c["verdict"])}</span></td></tr>'
    for c in claims)
cards = "\n".join(f"""<article id="c{c['n']}">
<h3><span class="num">{c['n']}</span> {e(c['topic'])} <span class="v {vclass(c['verdict'])}">{e(c['verdict'])}</span></h3>
<p class="cite"><a href="{e(c['bekiut'])}" target="_blank" rel="noopener">{e(c['ref'])}</a> on Bekiut · <a href="{e(c['sefaria'])}" target="_blank" rel="noopener">text on Sefaria</a></p>
<blockquote><p class="he" lang="he" dir="rtl">{e(c['he'])}</p><p class="en">{e(c['en'])}</p><p class="small">William Davidson edition</p></blockquote>
<dl>
<dt>{COL_CLAIM}</dt><dd>{e(c['claim'])}</dd>
<dt>{COL_LEW}</dt><dd><a href="{e(c['lew_url'])}" target="_blank" rel="noopener">{e(c['lew_label'])}</a> · {e(c['lewysohn'])}</dd>
<dt>Current zoology</dt><dd>{e(c['modern'])}</dd>
<dt>{COL_VERDICT}</dt><dd><strong>{e(c['verdict'])}.</strong> {e(c['verdict_note'])}</dd>
</dl>
</article>""" for c in claims)
counts = {}
for c in claims:
    counts[vclass(c["verdict"])] = counts.get(vclass(c["verdict"]), 0) + 1
intro_html = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", md_links(INTRO))
textnote_html = re.sub(r"`([^`]+)`", r"<code>\1</code>", e(TEXTNOTE))

page = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Talmud Zoology Fact-check</title>
<style>
:root {{ --bg:#fbfaf7; --fg:#1d1d1b; --muted:#66645e; --line:#e3e0d8; --card:#ffffff; --link:#1f5fa8;
  --t-bg:#e3f2e6; --t-fg:#1d6b33; --f-bg:#f8e1df; --f-fg:#a3271d; --p-bg:#fbefd5; --p-fg:#8a5a00; }}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#17171a; --fg:#e8e6e1; --muted:#a19e96;
  --line:#33333a; --card:#1f1f24; --link:#7fb2ee; --t-bg:#1d3a25; --t-fg:#8fdba4; --f-bg:#43201d; --f-fg:#f2a49b;
  --p-bg:#3f3218; --p-fg:#f0c873; }} }}
* {{ box-sizing:border-box; }}
body {{ margin:0; background:var(--bg); color:var(--fg); font:16px/1.55 Georgia, "Times New Roman", serif; }}
main {{ max-width:960px; margin:0 auto; padding:24px 16px 64px; }}
h1 {{ font-size:1.7rem; margin:.2em 0 .4em; }} h2 {{ margin-top:2em; border-bottom:1px solid var(--line); padding-bottom:.2em; }}
a {{ color:var(--link); }} .small, .cite {{ color:var(--muted); font-size:.85rem; }}
code {{ font-size:.85em; }}
.tally {{ display:flex; gap:8px; flex-wrap:wrap; margin:1em 0; }}
.wrap {{ overflow-x:auto; }}
table {{ border-collapse:collapse; width:100%; font-size:.92rem; background:var(--card); }}
th, td {{ border:1px solid var(--line); padding:6px 8px; text-align:left; vertical-align:top; }}
th {{ font-family:system-ui, sans-serif; font-size:.8rem; text-transform:uppercase; letter-spacing:.03em; color:var(--muted); }}
.v {{ display:inline-block; font:600 .75rem/1.4 system-ui, sans-serif; padding:1px 8px; border-radius:10px; vertical-align:middle; }}
.v.t {{ background:var(--t-bg); color:var(--t-fg); }} .v.f {{ background:var(--f-bg); color:var(--f-fg); }} .v.p {{ background:var(--p-bg); color:var(--p-fg); }}
article {{ background:var(--card); border:1px solid var(--line); border-radius:8px; padding:12px 18px; margin:18px 0; }}
article h3 {{ margin:.3em 0; font-size:1.15rem; }}
.num {{ color:var(--muted); font-family:system-ui, sans-serif; margin-right:4px; }}
blockquote {{ margin:10px 0; padding:8px 14px; border-left:3px solid var(--line); }}
.he {{ font-family:"SBL Hebrew", "Ezra SIL", "Frank Ruehl CLM", "David", serif; font-size:1.15rem; margin:.2em 0 .5em; }}
.en {{ font-style:italic; margin:.2em 0; }}
dt {{ font:600 .78rem system-ui, sans-serif; text-transform:uppercase; letter-spacing:.03em; color:var(--muted); margin-top:.7em; }}
dd {{ margin:.15em 0 0; }}
ul.src li {{ margin:.3em 0; }}
</style></head>
<body><main>
<h1>{e(TITLE)}</h1>
<p>{intro_html}</p>
<p class="small">{textnote_html}</p>
<div class="tally"><span class="v t">True / mostly true: {counts.get('t', 0)}</span><span class="v p">Partly true: {counts.get('p', 0)}</span><span class="v f">False / mostly false: {counts.get('f', 0)}</span></div>
<h2>Summary</h2>
<div class="wrap"><table>
<thead><tr><th>#</th><th>{COL_CLAIM}</th><th>{COL_CITE}</th><th>{COL_LEW}</th><th>{COL_VERDICT}</th></tr></thead>
<tbody>
{summary_rows}
</tbody></table></div>
<h2>Claims</h2>
{cards}
<h2>Sources for the modern data</h2>
<ul class="src">{''.join(f'<li>{md_links(s)}</li>' for s in sources)}</ul>
</main></body></html>
"""
(ROOT / "docs").mkdir(exist_ok=True)
(ROOT / "docs" / "index.html").write_text(page, encoding="utf-8")

# validate
back = list(csv.DictReader(open(ROOT / "factcheck.csv", encoding="utf-8-sig")))
assert len(back) == len(claims) == 20, len(back)
assert all(r["Sefaria: Hebrew/Aramaic (Davidson)"] for r in back)
assert [c["n"] for c in claims] == list(range(1, 21))
print("ok:", len(back), "rows; tally", counts)
