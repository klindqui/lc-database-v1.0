# LC Database

## Overview

The LC Database project provides an automated data ingestion pipeline for importing CSV sensor data from a Google Shared Drive into a Neon PostgreSQL database.

The current implementation focuses on the **Data_6_MEMS** dataset and provides:

- Automated synchronization from Google Drive
- CSV validation
- PostgreSQL bulk uploads using COPY
- Duplicate prevention
- Automatic file organization
- Pipeline logging
- Scheduled execution every 5 minutes

---

# Current Pipeline

Google Shared Drive
        ↓
RClone Sync
        ↓
runtime/staging
        ↓
Watcher
        ↓
Uploader
        ↓
Neon PostgreSQL

---

# Repository Structure

```
data_6_mems/
    scripts/
    runtime/
    logs/

config/

documents/

venv/
```

---

# Current Status

✔ Automated Google Drive synchronization

✔ Automated database uploads

✔ Duplicate prevention

✔ Automatic scheduling

✔ Logging

✔ Failure handling

✔ Documentation

---

# Documentation

- architecture.md
- vm_setup.md
- testing_checklist.md
- upload_results.md
- future_log_exports.md

---

# Future Improvements

- Additional ingestion pipelines
- Database roles and permissions
- GitHub log export
- Automatic run summaries
- Lock file protection