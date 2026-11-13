# Data Quality Auditor

A Python tool that audits annotation and research datasets for the errors that quietly ruin training and evaluation data: missing values, duplicate ids, invalid labels, bad timestamps, and out-of-range scores. It also measures agreement between two annotators with Cohen's kappa.

Built for Data QA Analyst, Data Annotator, and AI Evaluation roles. All data is synthetic.

## Why this exists

Annotation datasets often contain inconsistent labels, missing values, duplicates, and invalid records. Catching those before training or evaluation is exactly the QA work I do at TELUS Digital — a clean dataset is worth more than a bigger dirty one.

## What it checks

| Check | What it finds |
|---|---|
| Missing values | Rows with an empty label or field |
| Duplicates | Extra rows sharing the same `record_id` |
| Invalid labels | Labels not in the allowed set in the schema |
| Schema | Required columns missing from the file |
| Timestamps | Unparsable dates, and `reviewed_at` before `created_at` |
| Outliers | Numeric values outside their valid range (e.g. confidence over 100) |
| Agreement | Cohen's kappa between two annotators on the same items |

## Run it

```bash
pip install -r requirements.txt
python -m src.auditor.cli validate \
  --input data/annotations_sample.csv \
  --schema schemas/annotation.json \
  --output reports/audit.json --report-md reports/audit.md
python -m pytest -q
```

## Sample result

See `reports/sample_audit.md` — on the 11-row synthetic sample, 6 issues: 1 missing label, 1 duplicate id, 1 invalid label (`fish`, not in `cat / dog / bird`), 1 unparsable timestamp, 1 timestamp out of order, and 1 confidence score of 150.

## Structure

```
data-quality-auditor/
├── src/auditor/
│   ├── checks.py       # one small function per check
│   ├── agreement.py    # Cohen's kappa
│   ├── report.py       # audit_dataset + Markdown/JSON reports
│   └── cli.py          # `validate` command
├── data/annotations_sample.csv
├── schemas/annotation.json
├── tests/test_checks.py
├── tests/test_agreement_report.py
├── reports/sample_audit.md
├── .github/workflows/ci.yml
├── requirements.txt
└── LICENSE
```

## How to explain this in an interview

> "I built a CLI that audits an annotation CSV against a JSON schema. It flags missing labels, duplicate record ids, labels outside the allowed set, bad or out-of-order timestamps, and out-of-range scores, then writes a JSON and a Markdown audit report with the failing record ids. I also added Cohen's kappa, so you can check whether two annotators actually agree before trusting either set of labels. On the synthetic sample it finds 6 issues in 11 rows. The checks are small separate functions, so adding a new rule is one function plus one test."

## Limitations

- A checksum / range check verifies integrity, not correctness: a confidence of 90 can still be wrong. Document the range you chose and why.
- Kappa needs two annotators labelling the same items, in the same order.
- Synthetic data only. Do not upload employer, client, or proprietary annotation data.

## Skills

Data quality, annotation QA, Python, Pandas, pytest, GitHub Actions, CLI design.
