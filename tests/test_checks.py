"""Tests for the checks in src/auditor/checks.py.

Each test uses a tiny DataFrame built in the test itself, so a
failure points straight at the check that broke — not at the sample CSV.
"""
import pandas as pd

from src.auditor.checks import (
    find_duplicates,
    find_invalid_labels,
    find_missing,
    find_outliers,
    validate_schema,
    validate_timestamps,
)


def _df():
    return pd.DataFrame(
        {
            "record_id": [1, 2, 2, 3],
            "label": ["cat", None, "fish", "dog"],
            "confidence": [90, 80, 150, 70],
            "created_at": ["2026-01-05T09:00:00", "2026-01-05T09:00:00", "2026-01-05T09:00:00", "2026-01-05T09:00:00"],
            "reviewed_at": ["2026-01-05T09:10:00", "2026-01-05T09:10:00", "2026-01-05T08:00:00", "not-a-date"],
        }
    )


def test_find_missing_counts_empty_label():
    assert len(find_missing(_df(), ["label"])) == 1


def test_find_duplicates_keeps_first_copy():
    dupes = find_duplicates(_df())
    assert len(dupes) == 1
    assert dupes.iloc[0]["record_id"] == 2


def test_find_invalid_labels_flags_fish():
    bad = find_invalid_labels(_df(), allowed=["cat", "dog", "bird"])
    assert len(bad) == 1
    assert bad.iloc[0]["label"] == "fish"


def test_validate_schema_lists_missing_column():
    assert validate_schema(_df(), ["record_id", "label", "source"]) == ["source"]


def test_validate_timestamps_out_of_order_and_unparsable():
    result = validate_timestamps(_df())
    assert len(result["out_of_order"]) == 1
    assert len(result["unparsable"]) == 1


def test_find_outliers_flags_confidence_over_100():
    out = find_outliers(_df(), "confidence", 0, 100)
    assert len(out) == 1
    assert out.iloc[0]["confidence"] == 150
