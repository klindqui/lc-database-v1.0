# Upload Results

## Summary

Testing Date: June 2026

| Item | Result |
|------|--------|
| CSV Files Synchronized | 76 |
| CSV Files Uploaded | 73 |
| Files Rejected | 3 |
| Rows Imported | 2,631,529 |

---

## Timestamp Coverage

Earliest:

2026-02-19

Latest:

2026-06-23

---

## Failed Files

The following files were intentionally rejected by the uploader:

- mems_2026_03_19.csv
- mems_2026_04_16.csv
- mems_2026_06_01.csv

Reason:

Each file contained only a CSV header and no measurement data.

The pipeline automatically:

- rejected the upload
- logged the failure
- moved the file into runtime/failed

No manual intervention was required.

---

## Validation Result

The ingestion pipeline successfully completed a full historical upload and is ready for team testing.