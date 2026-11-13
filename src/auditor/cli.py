"""Command line: audit an annotation CSV against a schema.

Example (from the repo root):
    python -m src.auditor.cli validate \
      --input data/annotations_sample.csv \
      --schema schemas/annotation.json \
      --output reports/audit.json --report-md reports/audit.md
"""
import argparse
import json
from pathlib import Path

from .report import audit_file, to_markdown


def main():
    parser = argparse.ArgumentParser(description="Audit an annotation dataset.")
    sub = parser.add_subparsers(dest="command", required=True)
    validate = sub.add_parser("validate", help="Validate a CSV against a schema.")
    validate.add_argument("--input", required=True, help="CSV file to audit.")
    validate.add_argument("--schema", required=True, help="JSON schema file.")
    validate.add_argument("--output", default="reports/audit.json", help="JSON report path.")
    validate.add_argument("--report-md", default="reports/audit.md", help="Markdown report path.")
    args = parser.parse_args()

    result = audit_file(args.input, args.schema)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2))
    md_path = Path(args.report_md)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(to_markdown(result))
    print(to_markdown(result))
    print(f"JSON report: {output}")
    return result


if __name__ == "__main__":
    main()
