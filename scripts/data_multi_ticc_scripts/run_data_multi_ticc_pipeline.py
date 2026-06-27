import argparse
import logging
import subprocess
from pathlib import Path

BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_multi_ticc"

LOG_FILE = PIPELINE / "logs" / "pipeline.log"

PYTHON = BASE / "venv" / "bin" / "python"
SYNC_SCRIPT = PIPELINE / "scripts" / "data_multi_ticc_sync.py"
WATCHER_SCRIPT = PIPELINE / "scripts" / "data_multi_ticc_fw.py"


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def run_step(name: str, command: list[str]) -> int:
    logging.info(f"WRAPPER_STEP_STARTED | step={name} | command={' '.join(command)}")

    result = subprocess.run(command, capture_output=True, text=True)

    if result.stdout:
        logging.info(f"WRAPPER_{name}_STDOUT | {result.stdout.strip()}")

    if result.stderr:
        logging.warning(f"WRAPPER_{name}_STDERR | {result.stderr.strip()}")

    if result.returncode == 0:
        logging.info(f"WRAPPER_STEP_SUCCESS | step={name}")
    else:
        logging.error(f"WRAPPER_STEP_FAILED | step={name} | returncode={result.returncode}")

    return result.returncode


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Data_Multi_TICC sync and watcher pipeline.")
    parser.add_argument("--all", action="store_true", help="Sync all CSVs instead of recent files.")
    parser.add_argument("--dry-run", action="store_true", help="Run sync/watcher in dry-run mode.")
    args = parser.parse_args()

    logging.info(f"PIPELINE_RUN_STARTED | all={args.all} | dry_run={args.dry_run}")

    sync_cmd = [str(PYTHON), str(SYNC_SCRIPT)]
    if args.all:
        sync_cmd.append("--all")
    if args.dry_run:
        sync_cmd.append("--dry-run")

    sync_code = run_step("SYNC", sync_cmd)
    if sync_code != 0:
        logging.error("PIPELINE_RUN_FAILED | failed_step=SYNC")
        return sync_code

    watcher_cmd = [str(PYTHON), str(WATCHER_SCRIPT)]
    if args.dry_run:
        watcher_cmd.append("--dry-run")

    watcher_code = run_step("WATCHER", watcher_cmd)
    if watcher_code != 0:
        logging.error("PIPELINE_RUN_FAILED | failed_step=WATCHER")
        return watcher_code

    logging.info("PIPELINE_RUN_SUCCESS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())