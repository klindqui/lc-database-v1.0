# for data_multi_ticc 
# staging --> vm --> database
# validate CSV, then upload to database 
# only use on vm

import argparse
import csv
import io
import logging
import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg import connect
from psycopg.rows import dict_row

BASE = Path.home() / "lc-database"
PIPELINE = BASE / "data_multi_ticc"

LOG_FILE = PIPELINE / "logs" / "pipeline.log"
ENV_FILE = BASE / "config" / ".env"

TABLE = "public.data_multi_ticc"

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)


def db_url() -> str:
    load_dotenv(ENV_FILE)
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL is not set in ~/lc-database/config/.env")
    return url


def parse_table(raw: str) -> tuple[str, str]:
    if "." in raw:
        schema, table = raw.split(".", 1)
        return schema.strip(), table.strip()
    return "public", raw.strip()


def get_columns(schema: str, table: str) -> list[str]:
    query = """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = %s
          AND table_name = %s
        ORDER BY ordinal_position;
    """

    with connect(db_url(), row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, (schema, table))
            rows = cur.fetchall()

    if not rows:
        raise RuntimeError(f"Table not found or no permission: {schema}.{table}")

    return [
        row["column_name"]
        for row in rows
        if row["column_name"].lower() != "id"
    ]


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

    cleaned_header = [col.strip() for col in header]
    header_lower = [col.lower() for col in cleaned_header]

    valid_headers = [
        ["tstamp", "channel", "value"],
        ["tstamp", "channel", "phase_val"],
    ]

    if header_lower not in valid_headers:
        raise RuntimeError(
            "incorrect format. "
            "Expected one of: "
            f"{valid_headers}, got={cleaned_header}"
        )

    # Normalize the third column name so PostgreSQL always receives "value"
    if header_lower == ["tstamp", "channel", "phase_val"]:
        cleaned_header[2] = "value"

    new_header = ["source_file"] + cleaned_header
    writer.writerow(new_header)

    row_count = 0
    for row in reader:
        writer.writerow([path.name] + row)
        row_count += 1

    if row_count == 0:
        raise RuntimeError(
            f"{path.name}: CSV contains only a header row and no measurement data."
        )

    return new_header, output.getvalue().encode("utf-8")


def headers_match(csv_header: list[str], table_cols: list[str]) -> bool:
    csv_cols = [c.strip().lower() for c in csv_header]
    db_cols = [c.strip().lower() for c in table_cols]
    return csv_cols == db_cols


def copy_into_table(schema: str, table: str, table_cols: list[str], csv_bytes: bytes) -> None:
    columns = ", ".join(table_cols)

    copy_sql = (
        f"COPY {schema}.{table} ({columns}) "
        "FROM STDIN WITH (FORMAT csv, HEADER true)"
    )

    with connect(db_url()) as conn:
        with conn.cursor() as cur:
            with cur.copy(copy_sql) as copy:
                copy.write(csv_bytes)
        conn.commit()


def upload_file(path: Path, table_name: str, dry_run: bool) -> bool:
    if not path.exists():
        raise RuntimeError(f"File does not exist: {path}")

    if path.suffix.lower() != ".csv":
        raise RuntimeError(f"File is not a CSV: {path.name}")

    schema, table = parse_table(table_name)
    table_cols = get_columns(schema, table)

    csv_header, csv_bytes = read_csv_with_source_file(path)

    if not headers_match(csv_header, table_cols):
        raise RuntimeError(f"Header mismatch. CSV={csv_header} TABLE={table_cols}")

    logging.info(
        f"CSV_VALIDATED | file={path.name} | table={schema}.{table} | bytes={len(csv_bytes)}"
    )

    print(f"VALID CSV: {path.name}")
    print(f"Rows prepared for upload into {schema}.{table}")

    if dry_run:
        print("DRY RUN: database upload skipped.")
        logging.info(f"DRY_RUN_UPLOAD_VALIDATED | file={path.name}")
        return True

    copy_into_table(schema, table, table_cols, csv_bytes)

    print(f"UPLOAD OK: {path.name}")
    logging.info(f"UPLOAD_OK | file={path.name} | table={schema}.{table}")

    return True


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upload a Data_Multi_TICC CSV into PostgreSQL."
    )

    parser.add_argument("path", help="Path to CSV file.")

    parser.add_argument(
        "--table",
        default=TABLE,
        help="Destination table. Default: public.data_multi_ticc"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate only. Do not upload."
    )

    args = parser.parse_args()

    try:
        upload_file(Path(args.path), args.table, args.dry_run)
        return 0

    except Exception as e:
        print(f"FAIL: {e}")
        logging.error(f"UPLOAD_FAILED | file={args.path} | error={e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())