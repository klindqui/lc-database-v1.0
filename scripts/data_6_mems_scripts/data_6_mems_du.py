# staging --> vm --> database
# validate CSV, then upload to database (currently disabled until Neon storage is expanded)
# only use on vm

import argparse
import csv
import io
import logging
import os
from pathlib import Path

from dotenv import load_dotenv

BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_6_mems"

LOG_FILE = PIPELINE / "logs" / "pipeline.log"
ENV_FILE = BASE / "config" / ".env"

TABLE = "public.data_6_mems"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def read_csv_with_source_file(path: Path) -> tuple[list[str], bytes]:
    content = path.read_bytes()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise RuntimeError(f"{path.name}: CSV must be UTF-8 encoded.") from e

    reader = csv.reader(io.StringIO(text))
    output = io.StringIO()
    writer = csv.writer(output)

    try:
        header = next(reader)
    except StopIteration:
        raise RuntimeError(f"{path.name}: CSV is empty.")

    new_header = ["source_file"] + header
    writer.writerow(new_header)

    row_count = 0
    for row in reader:
        writer.writerow([path.name] + row)
        row_count += 1

    if row_count == 0:
        raise RuntimeError(f"{path.name}: CSV has header but no data rows.")

    return new_header, output.getvalue().encode("utf-8")


def validate_csv(path: Path) -> bool:
    if not path.exists():
        raise RuntimeError(f"File does not exist: {path}")

    if not path.is_file():
        raise RuntimeError(f"Path is not a file: {path}")

    if path.suffix.lower() != ".csv":
        raise RuntimeError(f"File is not a CSV: {path.name}")

    header, csv_bytes = read_csv_with_source_file(path)

    logging.info(
        f"CSV_VALIDATED | file={path.name} | columns={header} | bytes={len(csv_bytes)}"
    )

    print(f"VALID CSV: {path.name}")
    print(f"Columns: {header}")
    print(f"Bytes prepared: {len(csv_bytes)}")

    return True


def upload_to_database(path: Path, table: str) -> bool:
    load_dotenv(ENV_FILE)

    database_url = os.environ.get("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in ~/lc-database/config/.env")

    # Database upload is intentionally disabled until Neon storage is expanded.
    logging.info(f"DB_UPLOAD_SKIPPED_FOR_NOW | file={path.name} | table={table}")
    print("Database upload is currently disabled until Neon storage is expanded.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate and eventually upload a Data_6_MEMS CSV into PostgreSQL."
    )

    parser.add_argument(
        "path",
        help="Path to CSV file."
    )

    parser.add_argument(
        "--table",
        default=TABLE,
        help="Destination table. Default: public.data_6_mems"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate CSV only. Do not upload to database."
    )

    args = parser.parse_args()
    path = Path(args.path)

    try:
        validate_csv(path)

        if args.dry_run:
            logging.info(f"DRY_RUN_UPLOAD_VALIDATED | file={path.name}")
            print("DRY RUN: upload skipped.")
            return 0

        upload_to_database(path, args.table)
        return 0

    except Exception as e:
        logging.error(f"UPLOAD_VALIDATION_FAILED | file={path} | error={e}")
        print(f"FAIL: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())