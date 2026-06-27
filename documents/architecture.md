# Pipeline Architecture

## Overview

The LC Database project currently consists of two independent ingestion pipelines that automatically transfer CSV sensor data from Google Shared Drives into a Neon PostgreSQL database.

Current pipelines:

- **Data_6_MEMS**
- **Data_Multi_TICC**

Although each pipeline processes different datasets, both follow the same ingestion architecture and operate independently.

---

# Overall Architecture

```
                     Google Shared Drives
                    /                    \
                   /                      \
                  ▼                        ▼
          Data_6_MEMS               Data_Multi_TICC
                │                          │
                ▼                          ▼
            RClone Sync                RClone Sync
                │                          │
                ▼                          ▼
         runtime/staging           runtime/staging
                │                          │
                ▼                          ▼
             Watcher                   Watcher
                │                          │
                ▼                          ▼
             Uploader                  Uploader
                │                          │
                └──────────────┬───────────┘
                               │
                               ▼
                     Neon PostgreSQL Database
```

---

# Pipeline Components

Each ingestion pipeline consists of four independent scripts.

## 1. Sync

Purpose:

```
Google Shared Drive
        │
        ▼
runtime/staging
```

Responsibilities:

- Connect to Google Shared Drive using RClone
- Synchronize new CSV files
- Support recent-file synchronization
- Support full historical synchronization
- Ignore unsupported folders
- Log synchronization activity

---

## 2. Watcher

Purpose:

```
runtime/staging
        │
        ▼
Process incoming files
```

Responsibilities:

- Wait for files to finish copying
- Verify files are stable
- Skip files already listed in `processed.txt`
- Automatically remove duplicate files from staging
- Call the uploader
- Move successful uploads to `runtime/uploaded`
- Move failed uploads to `runtime/failed`
- Log all processing activity

---

## 3. Uploader

Purpose:

```
CSV Validation
        │
        ▼
PostgreSQL COPY Upload
```

Responsibilities:

- Verify UTF-8 encoding
- Validate CSV headers
- Validate database schema
- Automatically insert the `source_file` column
- Upload using PostgreSQL COPY
- Log upload results

---

## Data_Multi_TICC Header Support

The uploader accepts either of the following headers:

```
tstamp,channel,value
```

or

```
tstamp,channel,phase_val
```

Files using `phase_val` are automatically normalized to `value` before upload into PostgreSQL.

All other formats are rejected and moved to `runtime/failed`.

---

## 4. Pipeline Wrapper

Each dataset includes a wrapper script that executes the complete ingestion workflow.

Workflow:

```
Sync
   │
   ▼
Watcher
   │
   ▼
Uploader
```

The wrapper coordinates the entire pipeline and records execution status in the pipeline log.

---

# Runtime Directories

Each pipeline maintains the same runtime structure.

## staging/

Temporary holding area for synchronized CSV files awaiting processing.

---

## uploaded/

Contains CSV files successfully imported into PostgreSQL.

---

## failed/

Contains CSV files rejected during processing.

Examples include:

- Invalid CSV headers
- Empty CSV files
- Database validation failures
- Unsupported file formats

---

# Logging

Each pipeline maintains two log files.

## pipeline.log

Records:

- Synchronization activity
- Validation
- Upload status
- Duplicate detection
- File movement
- Wrapper execution

---

## processed.txt

Tracks successfully imported files.

Purpose:

- Prevent duplicate uploads
- Remove previously processed files from staging
- Maintain pipeline history

---

# Scheduling

Both pipelines execute automatically using **systemd timers**.

Current schedule:

| Pipeline | Schedule |
|----------|----------|
| Data_6_MEMS | 08:00 UTC and 20:00 UTC |
| Data_Multi_TICC | 08:30 UTC and 20:30 UTC |

---

# Design Goals

The ingestion framework is designed to provide:

- Independent processing for multiple datasets
- Reliable synchronization
- Automated validation
- Efficient PostgreSQL bulk uploads
- Duplicate protection
- Automatic file organization
- Comprehensive logging
- Easy expansion to additional ingestion pipelines in the future

---

# Future Expansion

The architecture was intentionally designed so that new datasets can be added by creating another pipeline with the same structure:

```
dataset_name/
    scripts/
    runtime/
    logs/
```

Each additional dataset can reuse the existing architecture while maintaining independent processing, logging, scheduling, and database tables.