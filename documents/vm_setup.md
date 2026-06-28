# VM Setup Guide

## Purpose

This virtual machine acts as the middleware between the Google Shared Drives and the Neon PostgreSQL database.

Its responsibilities include:

- Synchronizing CSV files from Google Shared Drives
- Validating incoming data
- Uploading data into PostgreSQL
- Organizing processed files
- Maintaining pipeline logs
- Preventing duplicate uploads

The VM is **not intended to be permanent storage**. Its purpose is to automate ingestion while acting as a lightweight processing layer.

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

sudo apt install python3-venv python3-pip rclone git nano -y
```

---

# Project Structure

```text
~/lc-database
│
├── data_6_mems/
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
├── data_multi_ticc/
│   ├── scripts/
│   │   ├── data_multi_ticc_sync.py
│   │   ├── data_multi_ticc_fw.py
│   │   ├── data_multi_ticc_du.py
│   │   └── run_data_multi_ticc_pipeline.py
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
├── docs/
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

mkdir -p ~/lc-database/data_multi_ticc/scripts
mkdir -p ~/lc-database/data_multi_ticc/runtime/staging
mkdir -p ~/lc-database/data_multi_ticc/runtime/uploaded
mkdir -p ~/lc-database/data_multi_ticc/runtime/failed
mkdir -p ~/lc-database/data_multi_ticc/logs

mkdir -p ~/lc-database/config
mkdir -p ~/lc-database/docs

touch ~/lc-database/data_6_mems/logs/pipeline.log
touch ~/lc-database/data_6_mems/logs/processed.txt

touch ~/lc-database/data_multi_ticc/logs/pipeline.log
touch ~/lc-database/data_multi_ticc/logs/processed.txt

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

Verify available datasets:

```bash
rclone lsf LC_GD:Data_6_MEMS --files-only --max-depth 1

rclone lsf LC_GD:Data_Multi_TICC --files-only --max-depth 1
```

---

# Pipeline Overview

Each dataset follows the same ingestion workflow.

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

# Pipeline Components

Each dataset contains four scripts.

## Sync

Responsibilities:

- Synchronize CSV files
- Support recent-file sync
- Support historical sync
- Log synchronization

---

## Watcher

Responsibilities:

- Monitor staging folder
- Wait for stable files
- Skip duplicates
- Remove already processed files
- Call uploader
- Move uploaded files
- Move failed files
- Maintain processed.txt

---

## Uploader

Responsibilities:

- UTF-8 validation
- CSV validation
- Header validation
- Database schema validation
- Insert source_file column
- PostgreSQL COPY upload

The Data_Multi_TICC uploader accepts both:

```
tstamp,channel,value
```

and

```
tstamp,channel,phase_val
```

Automatically converting `phase_val` to `value` before upload.

---

## Wrapper

Responsibilities:

- Execute Sync
- Execute Watcher
- Record pipeline execution
- Log execution status

---

# Runtime Folders

## staging/

Temporary holding location for synchronized CSV files.

---

## uploaded/

Contains successfully uploaded CSV files.

---

## failed/

Contains rejected CSV files.

Examples include:

- Invalid formatting
- Empty CSVs
- Database validation failures
- Unsupported headers

---

# Logging

Each dataset maintains:

```
pipeline.log
processed.txt
```

Purpose:

- Pipeline history
- Upload tracking
- Duplicate prevention
- Failure reporting

---

# Automation

Automation is handled using **systemd timers**.

Current schedule:

| Pipeline | Schedule |
|----------|----------|
| Data_6_MEMS | 08:00 UTC / 20:00 UTC |
| Data_Multi_TICC | 08:30 UTC / 20:30 UTC |

The timers automatically execute each pipeline wrapper without manual intervention.

---

# Testing Commands

Example commands:

```bash
python data_6_mems_sync.py --dry-run

python data_6_mems_fw.py --dry-run

python data_6_mems_du.py example.csv --dry-run

python run_data_6_mems_pipeline.py
```

```bash
python data_multi_ticc_sync.py --dry-run

python data_multi_ticc_fw.py --dry-run

python data_multi_ticc_du.py example.csv --dry-run

python run_data_multi_ticc_pipeline.py
```

---

# Design Principles

- Independent ingestion pipelines
- Reliable synchronization
- Efficient PostgreSQL COPY uploads
- Automatic duplicate prevention
- Automatic file organization
- Comprehensive logging
- Simple expansion to future datasets

---

# Database Security
- Database user roles and permissions

---

# Future Improvements

- Additional ingestion pipelines
- GitHub log exports
- Automated execution summaries
- Pipeline health monitoring
- Lock-file protection to prevent overlapping executions