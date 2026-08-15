# DocChrono Research Archive

[![CI](https://github.com/docchrono/docchrono-research-archive/actions/workflows/ci.yml/badge.svg)](https://github.com/docchrono/docchrono-research-archive/actions/workflows/ci.yml)
[![DocChrono 0.1.0](https://img.shields.io/badge/DocChrono-0.1.0-3776ab)](https://pypi.org/project/docchrono/0.1.0/)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

A complete, runnable example that turns a small fictional historical archive into a source-linked chronology and a durable DocChrono case file.

This repository uses the released [`docchrono` package](https://pypi.org/project/docchrono/) with no cloud AI service, API key, database, or model download.

## What this teaches

- Parse TXT, Markdown, RFC-822 email, and a machine-readable PDF together.
- Build a deterministic chronology with `Case.build(...)`.
- Confirm that every one of the four source documents contributes a dated event.
- Trace every event back to its source document and exact quotation.
- Preserve page and bounding-box provenance from PDF evidence.
- Save and reload the complete case without parsing the sources again.

All names, addresses, projects, assets, dates, and documents are synthetic.

## Run it

DocChrono 0.1.0 supports Python 3.11 through 3.13.

```bash
python -m venv .venv
# Windows: .venv\Scripts\python -m pip install -r requirements-dev.txt
.venv/bin/python -m pip install -r requirements-dev.txt

.venv/bin/python generate_data.py --check
.venv/bin/python demo.py
.venv/bin/python -m pytest -q
```

On Windows, replace `.venv/bin/python` with `.venv\Scripts\python`.

The demo writes `output/lantern.case.json`, loads it again, and proves semantic equality.

## Core API

```python
from pathlib import Path

from docchrono import Case

case = Case.build("data", strict=True)

for event in case.timeline:
    print(event.title, event.temporal)

Path("output").mkdir(exist_ok=True)
case.save("output/lantern.case.json")
reloaded = Case.load("output/lantern.case.json")
assert reloaded.data == case.data
```

`strict=True` makes a malformed or unsupported input fail the example instead of producing a partial case.

## Synthetic archive

| File | Format | Fictional fact being modeled |
| --- | --- | --- |
| `01_foundation_note.txt` | TXT | Eleanor Hart filed Project Lantern. |
| `02_board_minutes.md` | Markdown | Meridian Archive approved the project. |
| `03_dispatch.eml` | Email | Elias Stone transferred Asset `#L-17`. |
| `04_receipt_report.pdf` | PDF | The archive filed an asset receipt. |

Run `python generate_data.py` to recreate every byte. CI runs `--check` to ensure the committed fixtures still match the generator.

## Understanding provenance

An event is not treated as a free-floating fact. `case.evidence(event)` returns `EvidenceSpan` records with:

- the source document ID;
- exact raw and normalized offsets;
- the supporting quotation;
- page number and PDF boxes when available.

The demo verifies that every quotation exactly matches its immutable raw-document slice.

The full saved case also retains raw extracted text and source paths. Treat it as sensitive if
you adapt this example to real documents. `case.save_sanitized(...)` removes full document text
for sharing, but retains evidence quotations and cannot provide the same round-trip verification.

## Expected output

See [`expected_output.txt`](expected_output.txt). Counts and event titles are shown from the tested `docchrono==0.1.0` release.

## Scope

This is an extraction and provenance demonstration, not a claim that rules alone resolve historical ambiguity. DocChrono keeps source evidence inspectable so a researcher can review the result.

## License

Apache-2.0. The synthetic fixture data may be reused under the same license.
