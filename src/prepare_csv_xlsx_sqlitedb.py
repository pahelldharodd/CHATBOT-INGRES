from utils.prepare_sqlitedb_from_csv_xlsx import PrepareSQLFromTabularData
from utils.load_config import LoadConfig
import argparse
import os

APPCFG = LoadConfig()


def main():
    parser = argparse.ArgumentParser(description="Build SQLite DB from CSV/XLSX directory")
    parser.add_argument(
        "--dir",
        dest="files_dir",
        default=APPCFG.stored_csv_xlsx_directory,
        help="Directory with CSV/XLSX files (default: value from configs/app_config.yml)",
    )
    args = parser.parse_args()

    files_dir = args.files_dir
    if not os.path.isdir(files_dir):
        raise SystemExit(f"Input directory not found: {files_dir}")

    prep_sql_instance = PrepareSQLFromTabularData(files_dir)
    prep_sql_instance.run_pipeline()


if __name__ == "__main__":
    main()
