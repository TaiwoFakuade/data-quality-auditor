"""Data Quality Auditor — checks annotation datasets for common errors."""
from .checks import (
    find_duplicates,
    find_invalid_labels,
    find_missing,
    find_outliers,
    validate_schema,
    validate_timestamps,
)
from .agreement import cohens_kappa
from .report import audit_dataset, audit_file, to_markdown

__all__ = [
    "find_duplicates",
    "find_invalid_labels",
    "find_missing",
    "find_outliers",
    "validate_schema",
    "validate_timestamps",
    "cohens_kappa",
    "audit_dataset",
    "audit_file",
    "to_markdown",
]
