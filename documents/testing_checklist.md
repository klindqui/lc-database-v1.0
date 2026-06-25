# Data_6_MEMS Pipeline Testing Checklist

## VM

- [x] Ubuntu VM created
- [x] Python installed
- [x] Virtual environment configured

---

## Google Drive

- [x] RClone configured
- [x] Shared Drive connected
- [x] Recent synchronization tested
- [x] Full historical synchronization tested

---

## Database

- [x] Neon connection verified
- [x] CSV validation verified
- [x] PostgreSQL COPY upload verified
- [x] Duplicate constraint verified

---

## Pipeline

- [x] Sync script
- [x] Watcher script
- [x] Uploader script
- [x] Wrapper script
- [x] Logging
- [x] Failed file handling

---

## Automation

- [x] Wrapper executed successfully
- [x] systemd timer configured
- [x] Automatic execution every five minutes verified

---

## Final Validation

- [x] 76 files synchronized
- [x] 73 files uploaded
- [x] 3 files rejected correctly
- [x] 2,631,529 rows imported