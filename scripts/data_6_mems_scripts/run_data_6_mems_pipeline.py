import argparse
import logging
import subprocess
from pathlib import Path

BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_6_mems"

PYTHON = BASE / "venv" / "bin" / "python"

SYNC_SCRIPT = PIPELINE / "scripts" / "data_6_mems_sync.py"
WATCHER_SCRIPT = PIPELINE / "scripts" / "data_6_mems_fw.py"

LOG_FILE = PIPELINE / "logs" / "pipeline.log"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def run_command(cmd: list[str], label: str) -> bool:
    logging.info(f"WRAPPER_STEP_STARTED | step={label} | command={' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.stdout:
        print(result.stdout)
        logging.info(f"WRAPPER_{label}_STDOUT | {result.stdout.strip()}")

    if result.stderr:
        print(result.stderr)
        logging.warning(f"WRAPPER_{label}_STDERR | {result.stderr.strip()}")

    if result.returncode == 0:
        logging.info(f"WRAPPER_STEP_SUCCESS | step={label}")
        return True

    logging.error(f"WRAPPER_STEP_FAILED | step={label} | returncode={result.returncode}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the full Data_6_MEMS ingestion pipeline."
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Sync all root-level CSV files instead of only recent files."
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run sync and watcher in dry-run mode."
    )

    args = parser.parse_args()

    logging.info(
        f"PIPELINE_RUN_STARTED | all={args.all} | dry_run={args.dry_run}"
    )

    sync_cmd = [str(PYTHON), str(SYNC_SCRIPT)]

    if args.all:
        sync_cmd.append("--all")

    if args.dry_run:
        sync_cmd.append("--dry-run")

    watcher_cmd = [str(PYTHON), str(WATCHER_SCRIPT)]

    if args.dry_run:
        watcher_cmd.append("--dry-run")

    sync_ok = run_command(sync_cmd, "SYNC")

    if not sync_ok:
        logging.error("PIPELINE_RUN_FAILED | failed_step=SYNC")
        return 1

    watcher_ok = run_command(watcher_cmd, "WATCHER")

    if not watcher_ok:
        logging.error("PIPELINE_RUN_FAILED | failed_step=WATCHER")
        return 1

    logging.info("PIPELINE_RUN_SUCCESS")
    print("Pipeline run completed successfully.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())