# LC Database Testing Checklist

## Environment

### Virtual Machine

- [x] Google Cloud VM created
- [x] Ubuntu 24.04 LTS installed
- [x] Python installed
- [x] Virtual environment configured
- [x] Required packages installed
- [x] RClone installed
- [x] Git installed

---

## Google Drive

### RClone Configuration

- [x] Google Drive authenticated
- [x] Shared Drive connected
- [x] Data_6_MEMS folder accessible
- [x] Data_Multi_TICC folder accessible

---

# Database

## PostgreSQL

- [x] Neon database connected
- [x] Database credentials verified
- [x] Data_6_MEMS table created
- [x] Data_Multi_TICC table created

---

# Data_6_MEMS Pipeline

## Synchronization

- [x] Recent synchronization tested
- [x] Historical synchronization tested
- [x] Duplicate synchronization tested

---

## Uploader

- [x] UTF-8 validation
- [x] Header validation
- [x] CSV validation
- [x] PostgreSQL COPY upload
- [x] Duplicate constraint verified

---

## Watcher

- [x] Stable file detection
- [x] Duplicate detection
- [x] processed.txt tracking
- [x] Automatic upload
- [x] Uploaded folder movement
- [x] Failed folder movement
- [x] Removal of previously processed files from staging

---

## Wrapper

- [x] Sync execution
- [x] Watcher execution
- [x] Logging
- [x] Pipeline completion

---

# Data_Multi_TICC Pipeline

## Synchronization

- [x] Recent synchronization tested
- [x] Historical synchronization tested
- [x] Full Google Drive synchronization completed

---

## Uploader

- [x] UTF-8 validation
- [x] CSV validation
- [x] PostgreSQL COPY upload
- [x] Header validation
- [x] value header accepted
- [x] phase_val header accepted
- [x] Automatic phase_val normalization
- [x] Invalid headers rejected

---

## Watcher

- [x] Stable file detection
- [x] Duplicate detection
- [x] processed.txt tracking
- [x] Automatic upload
- [x] Uploaded folder movement
- [x] Failed folder movement
- [x] Removal of previously processed files from staging

---

## Wrapper

- [x] Sync execution
- [x] Watcher execution
- [x] Logging
- [x] Pipeline completion

---

# Automation

## systemd

- [x] Data_6_MEMS service created
- [x] Data_6_MEMS timer created
- [x] Data_Multi_TICC service created
- [x] Data_Multi_TICC timer created
- [x] Automatic execution verified

---

## Scheduling

- [x] Data_6_MEMS scheduled twice daily
- [x] Data_Multi_TICC scheduled twice daily
- [x] Timers enabled
- [x] Timers verified

---

# Logging

- [x] Synchronization logging
- [x] Upload logging
- [x] Failure logging
- [x] Wrapper logging
- [x] Duplicate logging
- [x] File movement logging

---

# Final Validation

## Data_6_MEMS

- [x] Historical upload completed
- [x] Duplicate prevention verified
- [x] Automatic scheduling verified
- [x] Production testing ready

---

## Data_Multi_TICC

- [x] Historical upload completed
- [x] Mixed header support verified
- [x] Invalid files rejected correctly
- [x] Duplicate prevention verified
- [x] Automatic scheduling verified
- [x] Production testing ready

---

# Overall Status

- [x] Both ingestion pipelines completed
- [x] Both pipelines independently tested
- [x] Automated synchronization verified
- [x] Automated uploads verified
- [x] Database integration verified
- [x] Scheduling verified
- [x] Logging verified
- [x] Ready for team testing