# LC Database

## Overview

The LC Database project provides an automated data ingestion system for importing CSV sensor data from Google Shared Drives into a Neon PostgreSQL database.

The current implementation includes two independent ingestion pipelines:

- **Data_6_MEMS** — Imports MEMS sensor data.
- **Data_Multi_TICC** — Imports Multi TICC sensor data.

Each pipeline automatically:

- Synchronizes CSV files from Google Shared Drive
- Validates CSV structure and encoding
- Uploads data into PostgreSQL using COPY
- Prevents duplicate processing
- Organizes processed files
- Logs all pipeline activity
- Executes automatically using systemd timers

---

# Current Architecture

```
Google Shared Drive
        │
        ▼
   RClone Sync
        │
        ▼
 runtime/staging
        │
        ▼
     Watcher
        │
        ▼
     Uploader
        │
        ▼
 Neon PostgreSQL
```

Both ingestion pipelines follow this architecture independently.

---

# Repository Structure

```
lc-database/
│
├── data_6_mems/
│   ├── scripts/
│   ├── runtime/
│   └── logs/
│
├── data_multi_ticc/
│   ├── scripts/
│   ├── runtime/
│   └── logs/
│
├── config/
│
├── docs/
│
└── venv/
```

---

# Current Features

## Data Synchronization

- Google Shared Drive synchronization using RClone
- Recent file synchronization
- Full historical synchronization
- Independent synchronization for each dataset

---

## CSV Validation

- UTF-8 validation
- Header validation
- Empty CSV detection
- Database schema validation
- Automatic source_file insertion

### Supported Data_Multi_TICC Formats

The uploader automatically accepts either of the following CSV headers:

```
tstamp,channel,value
```

or

```
tstamp,channel,phase_val
```

Files containing `phase_val` are automatically converted to `value` before upload.

---

## Upload Processing

- PostgreSQL COPY bulk uploads
- Automatic duplicate prevention
- Processed file tracking
- Automatic retry protection

---

## File Management

Successful uploads are moved into:

```
runtime/uploaded/
```

Invalid files are moved into:

```
runtime/failed/
```

Previously processed files are automatically removed from staging during future pipeline executions.

---

## Logging

Each pipeline maintains:

- pipeline.log
- processed.txt

Logs include:

- Synchronization activity
- Validation results
- Upload results
- Duplicate detection
- Failed uploads
- File movement
- Pipeline execution summaries

---

# Automation

Both pipelines execute automatically using **systemd timers**.

Current schedule:

| Pipeline | Schedule |
|----------|----------|
| Data_6_MEMS | 08:00 UTC / 20:00 UTC |
| Data_Multi_TICC | 08:30 UTC / 20:30 UTC |

---

## Roles and Users
- Role-based access control (RBAC)
- Dedicated service account for automated uploads

--

# Current Status

## Data_6_MEMS

- Complete
- Fully automated
- Production ready for testing

### Features

- Automated synchronization
- Automated uploads
- Duplicate prevention
- Failure handling
- Automatic scheduling
- Logging

---

## Data_Multi_TICC

- Complete
- Fully automated
- Production ready for testing

### Features

- Automated synchronization
- CSV validation
- Support for multiple CSV header formats
- Automated uploads
- Duplicate prevention
- Failure handling
- Automatic scheduling
- Logging

---

# Documentation

Repository documentation includes:

- README.md
- architecture.md
- vm_setup.md
- testing_checklist.md
- upload_results.md
- future_log_exports.md

---

# Future Improvements

Potential future enhancements include:

- Additional ingestion pipelines
- Automated GitHub log exports
- Pipeline execution summaries
- Lock-file protection to prevent overlapping executions
- Automated pipeline health monitoring
- Additional database validation checks

---

# Technologies

- Python
- PostgreSQL
- Neon
- Google Cloud Platform
- RClone
- systemd
- GitHub

---

# Project Goal

The goal of this project is to provide a reliable, maintainable, and extensible ingestion framework capable of automatically importing multiple sensor datasets into PostgreSQL with minimal manual intervention while maintaining comprehensive logging, validation, and duplicate protection.