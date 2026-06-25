# decides what to do with newly staged files: upload, move, log, etc.
# only works on the vm

import argparse
import logging
import shutil
import subprocess
import time
from pathlib import Path

BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_6_mems"

STAGING = PIPELINE / "runtime" / "staging"
UPLOADED = PIPELINE / "runtime" / "uploaded"
FAILED = PIPELINE / "runtime" / "failed"

LOG_FILE = PIPELINE / "logs" / "pipeline.log"
PROCESSED_FILE = PIPELINE / "logs" / "processed.txt"

UPLOADER = PIPELINE / "scripts" / "data_6_mems_du.py"
PYTHON = BASE / "venv" / "bin" / "python"

TABLE = "public.data_6_mems"

STABLE_CHECK_SECONDS = 2


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def file_key(path: Path) -> str:
    stat = path.stat()
    return f"{path.name}|{stat.st_size}"


def load_processed() -> set[str]:
    if not PROCESSED_FILE.exists():
        return set()

    return {
        line.strip()
        for line in PROCESSED_FILE.read_text().splitlines()
        if line.strip()
    }


def mark_processed(key: str) -> None:
    with PROCESSED_FILE.open("a") as f:
        f.write(key + "\n")


def is_stable(path: Path) -> bool:
    if not path.exists() or not path.is_file():
        return False

    size_1 = path.stat().st_size
    time.sleep(STABLE_CHECK_SECONDS)

    if not path.exists() or not path.is_file():
        return False

    size_2 = path.stat().st_size
    return size_1 == size_2


def move_with_overwrite(src: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src.name

    if dest.exists():
        stem = src.stem
        suffix = src.suffix
        counter = 1

        while True:
            new_dest = dest_dir / f"{stem}_{counter}{suffix}"
            if not new_dest.exists():
                dest = new_dest
                break
            counter += 1

    shutil.move(str(src), str(dest))
    return dest


def run_upload(csv_path: Path, dry_run: bool) -> bool:
    if dry_run:
        print(f"DRY RUN: would upload {csv_path.name}")
        logging.info(f"DRY_RUN_UPLOAD | file={csv_path.name}")
        return True

    cmd = [
        str(PYTHON),
        str(UPLOADER),
        "--table",
        TABLE,
        str(csv_path),
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"SUCCESS: {csv_path.name}")
        logging.info(f"UPLOAD_SUCCESS | file={csv_path.name} | stdout={result.stdout.strip()}")
        return True

    print(f"FAILURE: {csv_path.name}")
    logging.error(
        f"FILE_STATUS=FAILED | "
        f"file={csv_path.name} | "
        f"reason={result.stdout.strip()} {result.stderr.strip()} | "
        f"action=Moved to runtime/failed"
    )
    return False


def process_once(dry_run: bool) -> int:
    STAGING.mkdir(parents=True, exist_ok=True)
    UPLOADED.mkdir(parents=True, exist_ok=True)
    FAILED.mkdir(parents=True, exist_ok=True)
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    processed = load_processed()
    count = 0

    logging.info(f"WATCHER_SCAN_STARTED | staging={STAGING} | dry_run={dry_run}")

    for csv_path in sorted(STAGING.glob("*.csv")):
        if not csv_path.is_file():
            continue

        if not is_stable(csv_path):
            logging.warning(f"SKIPPED_NOT_STABLE | file={csv_path.name}")
            continue

        key = file_key(csv_path)

        if key in processed:
            logging.info(f"SKIPPED_ALREADY_PROCESSED | file={csv_path.name}")
            continue

        logging.info(f"DETECTED | file={csv_path.name}")

        ok = run_upload(csv_path, dry_run=dry_run)

        if ok:
            if not dry_run:
                mark_processed(key)
                logging.info(f"MARKED_PROCESSED | key={key}")

                moved_to = move_with_overwrite(csv_path, UPLOADED)
                logging.info(f"MOVED_UPLOADED | file={csv_path.name} | destination={moved_to}")
            else:
                logging.info(f"DRY_RUN_NOT_MARKED_PROCESSED | key={key}")
                logging.info(f"DRY_RUN_MOVE_UPLOADED | file={csv_path.name}")
        else:
            moved_to = move_with_overwrite(csv_path, FAILED)
            logging.info(f"MOVED_FAILED | file={csv_path.name} | destination={moved_to}")

        count += 1

    logging.info(f"WATCHER_SCAN_FINISHED | files_processed={count}")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Process staged Data_6_MEMS CSV files.")
    parser.add_argument("--dry-run", action="store_true", help="Do not upload or move files.")
    args = parser.parse_args()

    process_once(dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())