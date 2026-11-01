# talmud-zoology-factcheck

Zoological assertions of the Babylonian Talmud, checked against current zoology. Each claim is shown
with its exact Talmud segment, with what Ludwig Lewysohn said about it in *Die Zoologie des Talmuds*
(Frankfurt a. M. 1858), and with a verdict based on modern science. Lewysohn's 1858 judgement is
checked too: sometimes the Talmud is right and he is wrong (the camel's 12-month gestation).

**Page:** https://ezrabrand.github.io/talmud-zoology-factcheck/

A side project of [lewysohn-zoologie](https://github.com/EzraBrand/lewysohn-zoologie), the OCR and
English translation of Lewysohn ([reading edition](https://ezrabrand.github.io/lewysohn-zoologie/)).
Work in progress: small batches of claims, each checked by hand.

## Status (01-Nov-2026)

20 claims, all from the parts of Lewysohn already in English (pp. 1–158: general zoology and mammals).

| Verdict based on modern science | Claims |
|---|---|
| True / mostly true | 8 |
| Partly true | 3 |
| False / mostly false | 9 |

## Files

| File | What it is |
|---|---|
| `claims.json` | The source of truth: one record per claim (citation, claim, Lewysohn's comment and §, modern facts, verdict). Edit this. |
| `sources.json` | The sources for the modern data. |
| `build_report.py` | Builds `docs/index.html` (the page), `report.md` and `factcheck.csv` from the two files above and the Talmud text. |
| `fetch_sefaria.py` | Downloads the tractates that `claims.json` cites from the Sefaria export (see below). |
| `grep_daf.py` | Searches a downloaded tractate: `py grep_daf.py Chullin "ארנבת" --full`. |

## Talmud text and citations

- **Text:** the public [Sefaria export](https://github.com/Sefaria/Sefaria-Export) on Google Cloud Storage,
  `gs://sefaria-export/json/Talmud/Bavli/...`, William Davidson edition (Aramaic and English).
  `fetch_sefaria.py` downloads it anonymously with the `gcloud` CLI into `data/sefaria/`, which is not
  committed. The export date is in `data/sefaria_export_date.txt`.
- **Citations** use Sefaria's segment numbers (`Bekhorot 8a:13`) and link to
  [Bekiut](https://bekiut.com/), which uses the same numbering (`bekiut.com/talmud/Bekhorot/8a#13`).
  Each claim also links to the text on Sefaria.
- **Lewysohn** is cited by § and page of the 1858 edition. The links go to the § anchors of the English
  reading edition (`mammals.html#s119` for § 119).

## Method

1. Take a factual statement about animals from the Bavli, found through Lewysohn's §§.
2. Find the exact segment in the Sefaria text and quote it.
3. Record Lewysohn's comment (does he accept it, correct it, or explain it away?).
4. Check the claim against current zoology, with sources. Verdicts: true, mostly true, partly true,
   mostly false, false. A verdict judges the factual claim, not the moral or legal point the Talmud makes
   with it.
5. Some background values (for example the gestation of sheep or the hen's incubation) are standard
   reference figures not yet sourced one by one; `sources.json` lists them.

## Rebuild

```
py -3.13 fetch_sefaria.py
py -3.13 build_report.py
```

Python 3.13, standard library only; `gcloud` for the download.

## Licence

Code and the fact-check text: MIT (see `LICENSE`). The Talmud quotes are from the William Davidson
Talmud on Sefaria, licensed CC BY-NC.
