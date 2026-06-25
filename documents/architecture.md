# Pipeline Architecture

## Overview

The Data_6_MEMS pipeline automatically transfers CSV files from a Google Shared Drive into a Neon PostgreSQL database.

```
Google Shared Drive
        │
        ▼
RClone Sync
(sync every 5 minutes)
        │
        ▼
runtime/staging
        │
        ▼
Watcher
        │
        ├── Validate CSV
        ├── Check processed.txt
        ├── Add source_file column
        ├── Upload using PostgreSQL COPY
        │
        ├── Success
        │       ▼
        │   runtime/uploaded
        │
        └── Failure
                ▼
        runtime/failed
```

---

## Components

### Sync

Downloads new CSV files from Google Drive into the staging folder.

---

### Watcher

Processes newly synchronized files.

Responsibilities:

- Wait for files to finish copying
- Skip previously processed files
- Call the uploader
- Organize successful and failed files

---

### Uploader

Responsible for:

- CSV validation
- UTF-8 verification
- Header validation
- Adding source_file
- PostgreSQL COPY upload

---

### Scheduler

A systemd timer executes the wrapper script every five minutes.

The wrapper performs:

1. Synchronization
2. Upload processing
3. Logging