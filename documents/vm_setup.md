# VM Setup Guide

## Purpose

This virtual machine acts as the middleware between the Google Shared Drive and the Neon PostgreSQL database. It is responsible for automatically synchronizing, validating, and uploading CSV files into the database.

The VM is **not intended to be permanent storage**. Its primary purpose is to process incoming data and maintain pipeline logs.

---

# VM Information

| Setting | Value |
|---------|-------|
| Provider | Google Cloud Platform (GCP) |
| Operating System | Ubuntu 24.04 LTS Minimal (x86/64) |
| Machine Type | e2-small |
| Region | us-west1 |
| Disk Size | 20 GB |

---

# Initial Package Installation

```bash
sudo apt update

sudo apt install python3-venv python3-pip rclone git -y
```

---

# Project Structure

```text
~/lc-database
│
├── data_6_mems/
│   │
│   ├── scripts/
│   │   ├── data_6_mems_sync.py
│   │   ├── data_6_mems_fw.py
│   │   ├── data_6_mems_du.py
│   │   └── run_data_6_mems_pipeline.py
│   │
│   ├── runtime/
│   │   ├── staging/
│   │   ├── uploaded/
│   │   └── failed/
│   │
│   └── logs/
│       ├── pipeline.log
│       └── processed.txt
│
├── config/
│   ├── .env
│   ├── rclone.conf.backup
│   └── rclone_reconnect_notes.md
│
└── venv/
```

---

# Create Folder Structure

```bash
mkdir -p ~/lc-database/data_6_mems/scripts

mkdir -p ~/lc-database/data_6_mems/runtime/staging
mkdir -p ~/lc-database/data_6_mems/runtime/uploaded
mkdir -p ~/lc-database/data_6_mems/runtime/failed

mkdir -p ~/lc-database/data_6_mems/logs

mkdir -p ~/lc-database/config

touch ~/lc-database/data_6_mems/logs/pipeline.log
touch ~/lc-database/data_6_mems/logs/processed.txt
touch ~/lc-database/config/.env
```

---

# Python Environment

```bash
cd ~/lc-database

python3 -m venv venv

source venv/bin/activate

pip install psycopg[binary]
pip install python-dotenv
```

Verify installation:

```bash
which python

pip list
```

---

# Configure Google Drive (RClone)

Create a new remote:

```bash
rclone config
```

Configuration:

```text
Remote Name: LC_GD
Storage Type: Google Drive
Authentication: OAuth
Shared Drive: Yes
```

Verify access:

```bash
rclone lsd LC_GD:
```

Verify the Data_6_MEMS folder:

```bash
rclone lsf LC_GD:Data_6_MEMS --files-only --max-depth 1
```

---

# Pipeline Overview

```text
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

---

# Script Responsibilities

## data_6_mems_sync.py

Purpose:

```
Google Drive → runtime/staging
```

Responsibilities:

- Connect to Google Drive using RClone
- Synchronize CSV files
- Support recent-file synchronization
- Support full historical synchronization
- Ignore unsupported folders
- Log synchronization activity

Example:

```bash
python data_6_mems_sync.py
```

Recent files only.

```bash
python data_6_mems_sync.py --all
```

Historical synchronization.

---

## data_6_mems_fw.py

Purpose:

```
runtime/staging → processing
```

Responsibilities:

- Scan staging folder
- Wait for files to finish copying
- Skip previously processed files
- Call uploader
- Move successful uploads to `uploaded`
- Move failed uploads to `failed`
- Maintain `processed.txt`
- Log all activity

---

## data_6_mems_du.py

Purpose:

```
CSV validation + PostgreSQL upload
```

Responsibilities:

- Validate UTF-8 encoding
- Validate CSV structure
- Add `source_file`
- Validate database schema
- Upload using PostgreSQL COPY
- Log upload results

---

## run_data_6_mems_pipeline.py

Purpose:

Run the complete ingestion pipeline.

Workflow:

```
sync
    ↓
watcher
    ↓
uploader
```

This wrapper is executed manually or automatically by the scheduler.

---

# Runtime Folders

## staging/

Temporary holding location for newly synchronized CSV files.

---

## uploaded/

Contains files successfully uploaded into PostgreSQL.

---

## failed/

Contains files rejected during processing.

Reasons may include:

- Empty CSV (header only)
- Invalid formatting
- Database validation errors

---

# Logging

Pipeline log:

```text
~/lc-database/data_6_mems/logs/pipeline.log
```

Processed tracking:

```text
~/lc-database/data_6_mems/logs/processed.txt
```

Purpose:

- Record pipeline activity
- Record upload results
- Prevent duplicate processing

---

# Automation

The pipeline is fully automated using a **systemd timer**.

Every **5 minutes**, the timer executes:

```
run_data_6_mems_pipeline.py
```

The wrapper automatically performs:

1. Google Drive synchronization
2. CSV validation
3. Database upload
4. File organization
5. Pipeline logging

No manual execution is required during normal operation.

---

# Testing Commands

Test synchronization:

```bash
python data_6_mems_sync.py --dry-run
```

Test watcher:

```bash
python data_6_mems_fw.py --dry-run
```

Test uploader:

```bash
python data_6_mems_du.py example.csv --dry-run
```

Run the complete pipeline:

```bash
python run_data_6_mems_pipeline.py
```

---

# Lessons Learned

- Neon Free storage is insufficient for historical uploads.
- COPY-based uploads provide excellent performance for large datasets.
- Copy-based synchronization is more reliable than mounted Google Drive folders.
- Files should only be marked as processed after a successful upload.
- Empty CSV files should be rejected automatically.
- Duplicate protection should be enforced at the database level using a unique constraint.
- The VM should remain a processing layer rather than permanent storage.

---

# Future Improvements

- Add additional ingestion pipelines.
- Create database roles and user permissions.
- Export logs and run summaries to GitHub automatically.
- Generate automated upload reports.
- Add lock-file protection to prevent overlapping scheduled executions as the pipeline expands.