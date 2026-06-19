# VM Setup

## Purpose

This VM acts as the middleware between Google Drive and the Neon PostgreSQL database.

Responsibilities:
- Sync CSV files from Google Drive
- Stage files locally
- Validate files
- Upload files into PostgreSQL
- Log pipeline activity

---

## VM Information

Provider: Google Cloud Platform (GCP)

OS:
Ubuntu 24.04 LTS Minimal (x86/64)

Machine Type:
e2-small

Region:
us-west1

Disk:
20 GB

---

## Initial Package Installation

```bash
sudo apt update
sudo apt install python3-venv python3-pip rclone git -y
```

---

## Folder Structure

```text
~/lc-database
│
├── data_6_mems/
│   ├── scripts/
│   │   ├── data_6_mems_sync.py
│   │   ├── data_6_mems_fw.py
│   │   └── data_6_mems_du.py
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
│   └── .env
│
└── venv/
```

---

## Create Folder Structure

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

## Python Environment

```bash
cd ~/lc-database

python3 -m venv venv

source venv/bin/activate

pip install psycopg[binary]
pip install python-dotenv
```

Verification:

```bash
which python
pip list
```

---

## RClone Setup

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

Verify Data_6_MEMS:

```bash
rclone lsf LC_GD:Data_6_MEMS --files-only --max-depth 1
```

---

## Pipeline Architecture

```text
Google Drive
        ↓
data_6_mems_sync.py
        ↓
runtime/staging
        ↓
data_6_mems_fw.py
        ↓
data_6_mems_du.py
        ↓
Neon PostgreSQL
```

---

## Script Responsibilities

### data_6_mems_sync.py

Purpose:

```text
Google Drive → staging
```

Responsibilities:
- Connect to Google Drive using rclone
- Copy CSV files into staging
- Skip subfolders
- Support recent-file syncing
- Support full historical syncing
- Log all actions

Examples:

```bash
python data_6_mems_sync.py --dry-run
```

```bash
python data_6_mems_sync.py
```

```bash
python data_6_mems_sync.py --all
```

```bash
python data_6_mems_sync.py --all --dry-run
```

---

### data_6_mems_fw.py

Purpose:

```text
staging → process files
```

Responsibilities:
- Scan staging folder
- Detect new files
- Skip already processed files
- Verify files are stable
- Call uploader
- Move successful files to uploaded
- Move failed files to failed
- Maintain processed tracking
- Log all actions

Example:

```bash
python data_6_mems_fw.py --dry-run
```

---

### data_6_mems_du.py

Purpose:

```text
CSV validation + database upload
```

Responsibilities:
- Validate CSV
- Add source_file column
- Validate encoding
- Validate structure
- Prepare COPY upload data
- Upload into PostgreSQL

Example:

```bash
python data_6_mems_du.py example.csv --dry-run
```

---

## Runtime Folders

### staging/

Temporary holding area for newly synced files.

Files enter here after sync.

---

### uploaded/

Files move here after successful upload.

Used for audit/history.

---

### failed/

Files move here if upload fails.

Used for troubleshooting.

---

## Logging

Pipeline log:

```text
~/lc-database/data_6_mems/logs/pipeline.log
```

Processed tracking:

```text
~/lc-database/data_6_mems/logs/processed.txt
```

Purpose:

```text
pipeline.log
    Records all pipeline actions

processed.txt
    Prevents duplicate processing
```

---

## Testing Commands

Test sync:

```bash
python ~/lc-database/data_6_mems/scripts/data_6_mems_sync.py --dry-run
```

Test watcher:

```bash
python ~/lc-database/data_6_mems/scripts/data_6_mems_fw.py --dry-run
```

Test uploader:

```bash
python ~/lc-database/data_6_mems/scripts/data_6_mems_du.py \
~/lc-database/data_6_mems/runtime/staging/<file>.csv \
--dry-run
```

View logs:

```bash
tail -n 50 ~/lc-database/data_6_mems/logs/pipeline.log
```

View processed tracking:

```bash
cat ~/lc-database/data_6_mems/logs/processed.txt
```

View staging:

```bash
ls -lh ~/lc-database/data_6_mems/runtime/staging
```

View uploaded:

```bash
ls -lh ~/lc-database/data_6_mems/runtime/uploaded
```

View failed:

```bash
ls -lh ~/lc-database/data_6_mems/runtime/failed
```

---

## Known Issues / Lessons Learned

- Neon free tier is limited to 512 MB.
- Historical uploads require a paid Neon plan.
- The original rclone mount approach was abandoned.
- Copy-based syncing is more reliable and easier to troubleshoot.
- Dry-run mode must never update processed.txt.
- Files should only be marked processed after a confirmed successful upload.
- Google Drive subfolders should be ignored for the Data_6_MEMS pipeline.
- VM should remain a temporary processing layer, not permanent storage.

---

## Future Improvements

- Add additional data pipelines.
- Add database user roles.
- Add team access controls.
- Create exports folder for all logs and run summaries.
- Add GitHub export scripts.
- Add automated reporting.
- Improve duplicate prevention with database constraints.
- Add end-to-end automated testing.