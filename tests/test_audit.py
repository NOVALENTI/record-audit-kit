from pathlib import Path
import pytest
from record_audit.cli import audit_csv


def make_csv(tmp_path: Path, text: str) -> Path:
    path = tmp_path / "records.csv"
    path.write_text(text, encoding="utf-8")
    return path


def test_counts_missing_duplicate_and_invalid(tmp_path):
    p = make_csv(tmp_path, "id,email,created,owner\n1,a@example.com,2026-01-03,Sales\n1,invalid,2026-14-01,\n2,,2026-02-01,Ops\n")
    report = audit_csv(p, "id", email="email", date_column="created")
    assert report["row_count"] == 3
    assert report["duplicate_key_rows"] == 1
    assert report["missing_values_by_column"]["owner"] == 1
    assert report["missing_values_by_column"]["email"] == 1
    assert report["invalid_email_rows"] == 1
    assert report["invalid_iso_date_rows"] == 1
    assert "a@example.com" not in str(report)


def test_empty_csv_header(tmp_path):
    report = audit_csv(make_csv(tmp_path, "id,email\n"), "id", "email")
    assert report["row_count"] == 0
    assert report["duplicate_key_rows"] == 0


def test_unknown_columns_fail(tmp_path):
    with pytest.raises(ValueError, match="Missing required column"):
        audit_csv(make_csv(tmp_path, "id,email\n1,a@example.com\n"), "unknown")


def test_malformed_extra_columns_fail(tmp_path):
    with pytest.raises(ValueError, match="more fields"):
        audit_csv(make_csv(tmp_path, "id,email\n1,a@example.com,extra\n"), "id")


def test_keys_without_values_not_duplicates(tmp_path):
    p = make_csv(tmp_path, "id,email\n,first@example.com\n,second@example.com\n")
    report = audit_csv(p, "id")
    assert report["duplicate_key_rows"] == 0
    assert report["missing_values_by_column"]["id"] == 2


def test_reject_duplicate_headers(tmp_path):
    with pytest.raises(ValueError, match="Duplicate column"):
        audit_csv(make_csv(tmp_path, "id,id\n1,1\n"), "id")
