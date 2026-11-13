"""Run every check on a dataset and turn the result into a report."""
import json
from pathlib import Path

import pandas as pd

from .agreement import cohens_kappa
from .checks import (
    find_duplicates,
    find_invalid_labels,
    find_missing,
    find_outliers,
    validate_schema,
    validate_timestamps,
)


def audit_dataset(df, schema):
    """Audit one DataFrame against a schema dict. Returns a plain dict
    of counts and the failing record ids, so the JSON report is easy
    to read and the Markdown report is easy to skim."""
    required = schema.get("required_columns", list(df.columns))
    missing_columns = validate_schema(df, required)
    missing = find_missing(df, schema.get("check_columns", required))
    duplicates = find_duplicates(df, schema.get("id_column", "record_id"))
    invalid = find_invalid_labels(
        df,
        schema.get("label_column", "label"),
        schema.get("allowed_labels", []),
    )
    timestamps = validate_timestamps(
        df,
        schema.get("start_column", "created_at"),
        schema.get("end_column", "reviewed_at"),
    )
    outliers = pd.DataFrame()
    numeric = schema.get("numeric_range", {})
    if numeric:
        outliers = find_outliers(
            df,
            numeric.get("column", "confidence"),
            numeric.get("low", 0),
            numeric.get("high", 100),
        )
    result = {
        "total_rows": int(len(df)),
        "missing_columns": missing_columns,
        "missing_values": int(len(missing)),
        "missing_record_ids": [int(x) for x in missing["record_id"]] if "record_id" in df.columns else [],
        "duplicate_rows": int(len(duplicates)),
        "duplicate_record_ids": [int(x) for x in duplicates["record_id"]] if "record_id" in df.columns else [],
        "invalid_labels": int(len(invalid)),
        "invalid_record_ids": [int(x) for x in invalid["record_id"]] if "record_id" in df.columns else [],
        "timestamp_unparsable": len(timestamps["unparsable"]),
        "timestamp_out_of_order": len(timestamps["out_of_order"]),
        "outliers": int(len(outliers)),
        "outlier_record_ids": [int(x) for x in outliers["record_id"]] if "record_id" in df.columns and len(outliers) else [],
    }
    result["total_issues"] = (
        result["missing_values"]
        + result["duplicate_rows"]
        + result["invalid_labels"]
        + result["timestamp_unparsable"]
        + result["timestamp_out_of_order"]
        + result["outliers"]
    )
    return result


def audit_file(input_path, schema_path):
    """Load a CSV and its schema file, then audit it."""
    df = pd.read_csv(input_path)
    schema = json.loads(Path(schema_path).read_text())
    return audit_dataset(df, schema)


def to_markdown(result):
    """One-page audit report a reviewer can read without running code."""
    lines = [
        "# Audit Report",
        "",
        f"Rows checked: {result['total_rows']}",
        f"Total issues found: {result['total_issues']}",
        "",
        "## Issues by type",
        "",
        f"- Missing values: {result['missing_values']} (record ids: {result['missing_record_ids']})",
        f"- Duplicate rows: {result['duplicate_rows']} (record ids: {result['duplicate_record_ids']})",
        f"- Invalid labels: {result['invalid_labels']} (record ids: {result['invalid_record_ids']})",
        f"- Unparsable timestamps: {result['timestamp_unparsable']}",
        f"- Timestamps out of order: {result['timestamp_out_of_order']}",
        f"- Outliers: {result['outliers']} (record ids: {result['outlier_record_ids']})",
        "",
        "## Recommendation",
        "",
    ]
    if result["total_issues"] == 0:
        lines.append("No issues found. The dataset is ready to use.")
    else:
        lines.append(
            "Fix the rows listed above before training or evaluation: "
            "fill or drop missing labels, remove duplicate ids, correct "
            "invalid labels and timestamps, and check outlier scores "
            "against the original source."
        )
    if result["missing_columns"]:
        lines.append(f"Missing columns: {result['missing_columns']}")
    return "\n".join(lines) + "\n"


def agreement_report(labels_a, labels_b):
    """Kappa for two annotators' labels on the same items."""
    return {"cohens_kappa": round(cohens_kappa(labels_a, labels_b), 3)}
