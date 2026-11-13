"""Tests for agreement (Cohen's kappa) and the end-to-end audit report."""
import json
from pathlib import Path

from src.auditor.agreement import cohens_kappa
from src.auditor.report import audit_file, to_markdown

SAMPLE = Path(__file__).resolve().parents[1] / "data" / "annotations_sample.csv"
SCHEMA = Path(__file__).resolve().parents[1] / "schemas" / "annotation.json"


def test_cohens_kappa_perfect_agreement_is_one():
    assert cohens_kappa(["cat", "dog", "bird"], ["cat", "dog", "bird"]) == 1.0


def test_cohens_kappa_disagreement_is_lower():
    perfect = cohens_kappa(["cat", "dog", "bird", "cat"], ["cat", "dog", "bird", "cat"])
    partial = cohens_kappa(["cat", "dog", "bird", "cat"], ["cat", "dog", "cat", "cat"])
    assert partial < perfect
    assert -1.0 <= partial <= 1.0


def test_audit_sample_csv_counts_are_known():
    # 11 rows in the sample: 1 missing label, 1 duplicate id, 1 invalid
    # label, 1 unparsable timestamp, 1 out-of-order timestamp, 1 outlier.
    result = audit_file(str(SAMPLE), str(SCHEMA))
    assert result["total_rows"] == 11
    assert result["missing_values"] == 1
    assert result["duplicate_rows"] == 1
    assert result["invalid_labels"] == 1
    assert result["timestamp_unparsable"] == 1
    assert result["timestamp_out_of_order"] == 1
    assert result["outliers"] == 1
    assert result["total_issues"] == 6


def test_markdown_report_names_the_issue_counts():
    result = audit_file(str(SAMPLE), str(SCHEMA))
    text = to_markdown(result)
    assert "Rows checked: 11" in text
    assert "Total issues found: 6" in text
    assert "Missing values: 1" in text
