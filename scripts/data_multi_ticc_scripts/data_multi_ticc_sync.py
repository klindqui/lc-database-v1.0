# google drive --> vm
# note that this script only syncs root-level CSV files in the Data_Multi_Ticc folder, not subfolder
# not to be used locally, only on the 

import argparse
import logging
import subprocess
from pathlib import Path


BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_multi_ticc"

STAGING = PIPELINE / "runtime" / "staging"
LOG_FILE = PIPELINE / "logs" / "pipeline.log"

REMOTE_PATH = "LC_GD:Data_Multi_TICC"

DEFAULT_MAX_AGE = "2d"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def run_sync(max_age: str, dry_run: bool) -> int:
    STAGING.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        "rclone",
        "copy",
        REMOTE_PATH,
        str(STAGING),
        "--include",
        "*.csv",
        "--max-depth",
        "1",
        "--max-age",
        max_age,
        "--progress",
    ]

    if dry_run:
        cmd.append("--dry-run")

    logging.info(f"SYNC_STARTED | remote={REMOTE_PATH} | staging={STAGING} | max_age={max_age} | dry_run={dry_run}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
        logging.info(f"SYNC_STDOUT | {result.stdout.strip()}")

    if result.stderr:
        print(result.stderr)
        logging.warning(f"SYNC_STDERR | {result.stderr.strip()}")

    if result.returncode == 0:
        logging.info("SYNC_SUCCESS")
    else:
        logging.error(f"SYNC_FAILED | returncode={result.returncode}")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync recent root-level Data_Multi_TICC CSV files from Google Drive into local staging."
    )
    parser.add_argument("--max-age", default=DEFAULT_MAX_AGE, help="Only copy files modified within this age, e.g. 2d, 12h, 30m.")
    parser.add_argument("--all", action="store_true", help="Copy all root-level CSVs, ignoring max-age.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be copied without copying files.")

    args = parser.parse_args()

    max_age = "9999d" if args.all else args.max_age
    return run_sync(max_age=max_age, dry_run=args.dry_run)


if __name__ == "__main__":
    raise SystemExit(main())