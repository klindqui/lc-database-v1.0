import time
import logging
import subprocess
from pathlib import Path

BASE = Path.home() / "lc-database"

INCOMING = BASE / "mounts" / "data_6_mems"
LOG_FILE = BASE / "logs" / "data_6_mems.log"
PROCESSED_FILE = BASE / "logs" / "data_6_mems_processed.txt"

TABLE = "public.data_6_mems"
UPLOADER = BASE / "scripts" / "data_6_mems_du.py"
PYTHON = BASE / "venv" / "bin" / "python"

POLL_SECONDS = 10
STABLE_CHECK_SECONDS = 2


logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


def file_key(path: Path) -> str:
    stat = path.stat()
    relative_path = path.relative_to(INCOMING)
    return f"{relative_path}|{stat.st_size}"


def load_processed() -> set[str]:
    if not PROCESSED_FILE.exists():
        return set()

    return set(
        line.strip()
        for line in PROCESSED_FILE.read_text().splitlines()
        if line.strip()
    )


def mark_processed(key: str) -> None:
    with PROCESSED_FILE.open("a") as f:
        f.write(key + "\n")


def is_stable(path: Path) -> bool:
    try:
        if not path.exists() or not path.is_file():
            return False

        size_1 = path.stat().st_size
        time.sleep(STABLE_CHECK_SECONDS)

        if not path.exists() or not path.is_file():
            return False

        size_2 = path.stat().st_size
        return size_1 == size_2

    except OSError:
        return False


def run_upload_one(csv_path: Path) -> bool:
    cmd = [str(PYTHON), str(UPLOADER), "--table", TABLE, str(csv_path)]

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"SUCCESS: {csv_path.name}")
        logging.info(
            f"SUCCESS | file={csv_path} | table={TABLE} | stdout={result.stdout.strip()}"
        )
        return True

    print(f"FAILURE: {csv_path.name}")
    logging.error(
        f"FAILURE | file={csv_path} | table={TABLE} | "
        f"stderr={result.stderr.strip()} | stdout={result.stdout.strip()}"
    )
    return False


def main():
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROCESSED_FILE.parent.mkdir(parents=True, exist_ok=True)

    print(f"Watching mounted Google Drive folder: {INCOMING}")
    logging.info(f"WATCHER_STARTED | folder={INCOMING} | table={TABLE}")

    while True:
        try:
            processed = load_processed()

            for csv_path in sorted(INCOMING.glob("*.csv")):

                try:
                    relative_parts = csv_path.relative_to(INCOMING).parts

                    if relative_parts:
                        first_folder = relative_parts[0].lower()

                        if first_folder in {"old data", "pst"}:
                            continue

                except Exception:
                    continue

                if not csv_path.is_file():
                    continue

                if not is_stable(csv_path):
                    continue

                key = file_key(csv_path)

                if key in processed:
                    continue

                print(f"Detected new file: {csv_path}")
                logging.info(f"DETECTED | file={csv_path}")

                ok = run_upload_one(csv_path)

                if ok:
                    mark_processed(key)
                    logging.info(f"MARKED_PROCESSED | key={key}")

        except Exception as e:
            print(f"Watcher error: {e}")
            logging.exception(f"WATCHER_ERROR | error={e}")

        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    main()