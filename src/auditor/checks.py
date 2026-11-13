"""Data Quality Auditor — checks annotation / research datasets for common errors.

Each check is a small, plain function that takes a pandas DataFrame and
returns the rows (or columns) that failed, so you can explain every step
in an interview: what it checks, why it matters, and what to do next.
"""
import pandas as pd


def find_missing(df, columns=None):
    """Rows with an empty value in any of the given columns.

    Missing labels are the most common annotation error: a row with no
    label cannot be used for training or evaluation, and silently
    dropping it can bias the dataset.
    """
    columns = columns or list(df.columns)
    missing = df[df[columns].isna().any(axis=1)]
    return missing


def find_duplicates(df, id_column="record_id"):
    """Extra rows sharing the same record id (the first copy is kept)."""
    if id_column not in df.columns:
        return df.iloc[0:0]
    return df[df.duplicated(subset=[id_column], keep="first")]


def find_invalid_labels(df, label_column="label", allowed=None):
    """Rows whose label is present but not in the allowed label set."""
    allowed = allowed or []
    present = df[df[label_column].notna()]
    return present[~present[label_column].isin(allowed)]


def validate_schema(df, required_columns):
    """Columns that the schema requires but the file does not have."""
    return [c for c in required_columns if c not in df.columns]


def validate_timestamps(df, start_column="created_at", end_column="reviewed_at"):
    """Two timestamp problems, reported separately:

    - ``unparsable``: a value that is not a real date/time.
    - ``out_of_order``: reviewed_at earlier than created_at.
    """
    result = {"unparsable": [], "out_of_order": []}
    if start_column not in df.columns or end_column not in df.columns:
        return result
    for idx, row in df.iterrows():
        start = pd.to_datetime(row[start_column], errors="coerce")
        end = pd.to_datetime(row[end_column], errors="coerce")
        if pd.isna(start) or pd.isna(end):
            result["unparsable"].append(idx)
        elif end < start:
            result["out_of_order"].append(idx)
    return result


def find_outliers(df, column="confidence", low=0, high=100):
    """Rows where a numeric value falls outside its valid range.

    The default range (0–100) fits a confidence score. For other
    columns, pass the range that makes sense for that field — a
    checksum checks integrity, not correctness, so document the range
    you chose and why.
    """
    if column not in df.columns:
        return df.iloc[0:0]
    values = pd.to_numeric(df[column], errors="coerce")
    return df[(values < low) | (values > high)]
