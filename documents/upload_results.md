# Upload Results

## Summary

Testing Period: June 2026

---

# Data_6_MEMS

| Item | Result |
|------|--------|
| CSV Files Synchronized | 76 |
| CSV Files Uploaded | 73 |
| Files Rejected | 3 |
| Rows Imported | 2,631,529 |

---

## Timestamp Coverage

Earliest Timestamp

```
2026-02-19
```

Latest Timestamp

```
2026-06-23
```

---

## Rejected Files

The following files were intentionally rejected:

- Header-only CSV files
- Empty datasets

These files were automatically:

- Logged
- Rejected
- Moved to `runtime/failed`

No manual intervention was required.

---

# Data_Multi_TICC

| Item | Result |
|------|--------|
| CSV Files Synchronized | 113 |
| CSV Files Successfully Uploaded | 92 |
| Files Rejected | 21 |

---

## Supported CSV Formats

The uploader successfully accepted both formats:

```
tstamp,channel,value
```

and

```
tstamp,channel,phase_val
```

Files using the `phase_val` column were automatically converted to the PostgreSQL schema before upload.

---

## Rejected Files

Rejected files contained unsupported CSV formats, including historical files using alternate multi-channel layouts such as:

```
tstamp,ch_a,ch_b,ch_c,...
```

These files were automatically:

- Logged
- Rejected
- Moved to `runtime/failed`

No manual cleanup was required.

---

# Duplicate Protection

Both ingestion pipelines successfully prevented duplicate uploads through:

- Database constraints
- `processed.txt` tracking
- Automatic duplicate detection
- Automatic removal of previously processed files from the staging directory

---

# File Organization

Successful uploads were automatically moved into:

```
runtime/uploaded
```

Rejected uploads were automatically moved into:

```
runtime/failed
```

Previously processed files synchronized from Google Drive were automatically removed from staging before processing.

---

# Logging

Both pipelines successfully recorded:

- Synchronization activity
- CSV validation
- Upload success
- Upload failures
- Duplicate detection
- File movement
- Wrapper execution
- Pipeline completion

---

# Validation Results

The ingestion framework successfully demonstrated:

- Automated Google Drive synchronization
- PostgreSQL COPY uploads
- CSV validation
- UTF-8 validation
- Header validation
- Duplicate prevention
- Automatic file organization
- Pipeline logging
- Independent execution of multiple ingestion pipelines

---

# Final Status

Both ingestion pipelines have completed end-to-end testing and are ready for team use.

Current completed pipelines:

- ✅ Data_6_MEMS
- ✅ Data_Multi_TICC

Both pipelines are fully automated using systemd timers and execute independently according to their configured schedules.