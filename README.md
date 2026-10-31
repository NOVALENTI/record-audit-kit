# Record Audit Kit

A practical **Python data-quality CLI** for checking spreadsheets exported as CSV. Designed for operations, administrative, and data-entry workflows.

**Created by Valentino Herrera.**

## What it checks

- Missing values in every column
- Repeated non-empty record IDs
- Invalid email formats in a selected column
- Invalid ISO dates (`YYYY-MM-DD`) in a selected column
- Reports aggregate counts only; does not echo source record values
- **Read-only:** does not modify the source CSV

## Quick start

Requires Python 3.11+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[test]'
record-audit examples/sample_records.csv --key record_id --email email --date created_at
pytest -q
```

To save a report:

```bash
record-audit examples/sample_records.csv --key record_id --email email --date created_at --output audit-report.json
```

## Example output (synthetic data)

```json
{
  "column_count": 4,
  "duplicate_key_rows": 1,
  "invalid_email_rows": 1,
  "invalid_iso_date_rows": 1,
  "missing_values_by_column": {
    "created_at": 0,
    "email": 1,
    "record_id": 0,
    "status": 0
  },
  "row_count": 4
}
```

## Quality and privacy notes

- The demo records are fictional and used only for automated testing.
- Output includes the input **file name** and aggregate data-quality metrics, not customer row values.
- Email checking is a simple format check, not proof that an address exists.
- CSVs with unusually complex encodings or quoted records may require normalization before running.
- The tool is meant for quick data audits, not for replacing comprehensive ETL or data-governance systems.

## Rights and commercial use

Copyright © 2026 Valentino Herrera. All rights reserved. No open-source reuse license is granted for this original demo. Viewing and forking are subject to GitHub's terms and applicable law; commercial use or commissioned adaptations require a separate written agreement. For licensing discussions: **valentinoherreraofficial@gmail.com**. Viewing this repository does not create an automatic payment obligation.
