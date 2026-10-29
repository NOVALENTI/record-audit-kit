"""Read-only CSV auditing CLI: missing values, duplicates, email and ISO-date checks."""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from datetime import date
from pathlib import Path

EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def audit_csv(path: Path, key: str, email: str | None = None, date_column: str | None = None) -> dict:
    """Produce deterministic aggregate findings; never include source row values."""
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = csv.DictReader(stream)
        fields = rows.fieldnames or []
        if len(fields) != len(set(fields)):
            raise ValueError("Duplicate column names are not supported")
        for col in [key, email, date_column]:
            if col and col not in fields:
                raise ValueError(f"Missing required column: {col}")
        missing = Counter({f: 0 for f in fields})
        invalid_email = 0
        invalid_date = 0
        key_counts = Counter()
        count = 0
        for row in rows:
            if None in row:
                raise ValueError("CSV row contains more fields than the header")
            count += 1
            for col in fields:
                if not (row.get(col) or "").strip():
                    missing[col] += 1
            value = (row.get(key) or "").strip()
            if value:
                key_counts[value] += 1
            if email and (v := (row.get(email) or "").strip()) and not EMAIL_PATTERN.fullmatch(v):
                invalid_email += 1
            if date_column and (v := (row.get(date_column) or "").strip()):
                try:
                    date.fromisoformat(v)
                except ValueError:
                    invalid_date += 1
        duplicates = sum(n - 1 for n in key_counts.values() if n > 1)
        return {
            "source": path.name,
            "row_count": count,
            "column_count": len(fields),
            "missing_values_by_column": dict(missing),
            "duplicate_key_rows": duplicates,
            "invalid_email_rows": invalid_email,
            "invalid_iso_date_rows": invalid_date,
            "checks": {"primary_key": key, "email": email, "iso_date": date_column},
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit CSV quality without modifying source files")
    parser.add_argument("csv", type=Path, help="Input CSV file")
    parser.add_argument("--key", required=True, help="Column whose non-empty values should be unique")
    parser.add_argument("--email", help="Optional column to validate as email addresses")
    parser.add_argument("--date", help="Optional ISO date column (YYYY-MM-DD)")
    parser.add_argument("--output", type=Path, help="Optional destination for JSON report")
    args = parser.parse_args()
    try:
        report = audit_csv(args.csv, args.key, args.email, args.date)
    except (OSError, csv.Error, ValueError) as exc:
        parser.error(str(exc))
    result = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        args.output.write_text(result + "\n", encoding="utf-8")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
