import os
import csv
import io
import fnmatch
import argparse
from pathlib import Path

from psycopg import connect
from psycopg.rows import dict_row


def db_url() -> str:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL environment variable is not set.")
    return url


def parse_table(raw: str) -> tuple[str, str]:
    raw = raw.strip()

    if "." in raw:
        schema, table = raw.split(".", 1)
        return schema.strip(), table.strip()

    return "public", raw


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


def read_header_and_bytes(path: Path) -> tuple[list[str], bytes]:
    content = path.read_bytes()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as e:
        raise RuntimeError(f"{path.name}: CSV must be UTF-8 encoded.") from e

    input_file = io.StringIO(text)
    reader = csv.reader(input_file)

    output_file = io.StringIO()
    writer = csv.writer(output_file)

    try:
        header = next(reader)
    except StopIteration:
        raise RuntimeError(f"{path.name}: CSV is empty.")

    new_header = ["source_file"] + header
    writer.writerow(new_header)

    for row in reader:
        writer.writerow([path.name] + row)

    new_content = output_file.getvalue().encode("utf-8")

    return new_header, new_content


def header_matches_exact(header: list[str], table_cols: list[str]) -> bool:
    csv_cols = [col.strip().lower() for col in header]
    db_cols = [col.strip().lower() for col in table_cols]

    return csv_cols == db_cols


def iter_csv_files(path: Path, pattern: str) -> list[Path]:
    if path.is_file():
        return [path]

    if not path.is_dir():
        return []

    return sorted(
        p for p in path.iterdir()
        if p.is_file() and fnmatch.fnmatch(p.name, pattern)
    )


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


def upload_file(fpath: Path, schema: str, table: str, table_cols: list[str], strict: bool) -> bool:
    print(f"Uploading {fpath.name} ... ", end="")

    try:
        header, csv_bytes = read_header_and_bytes(fpath)

        if strict and not header_matches_exact(header, table_cols):
            raise RuntimeError(f"Header mismatch. CSV={header} TABLE={table_cols}")

        copy_into_table(schema, table, table_cols, csv_bytes)

        print("OK")
        return True

    except Exception as e:
        print("FAIL")
        print(f"  {e}")
        return False


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Upload one CSV file or a folder of CSVs into PostgreSQL using COPY."
    )

    parser.add_argument(
        "path",
        help="CSV file path or folder path containing CSV files."
    )

    parser.add_argument(
        "--table",
        required=True,
        help="Destination table, for example: public.data_6_mems"
    )

    parser.add_argument(
        "--pattern",
        default="*.csv",
        help='For folder uploads. Default: "*.csv"'
    )

    parser.add_argument(
        "--no-strict-header",
        action="store_true",
        help="Disable exact CSV header match check."
    )

    args = parser.parse_args()

    schema, table = parse_table(args.table)
    strict = not args.no_strict_header
    target = Path(args.path)

    try:
        table_cols = get_columns(schema, table)
    except Exception as e:
        print(f"ERROR: {e}")
        return 2

    files = iter_csv_files(target, args.pattern)

    if not files:
        print(f"No CSV files found at {target} with pattern {args.pattern}")
        return 1

    success_count = 0
    fail_count = 0

    for fpath in files:
        if upload_file(fpath, schema, table, table_cols, strict):
            success_count += 1
        else:
            fail_count += 1

    print(f"\nDone. Success={success_count} Failed={fail_count}")

    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())