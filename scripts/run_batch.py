import argparse

from ingestion.batch import Batch
from ingestion.ingest import ingest_batch


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest one NYC Taxi batch.")
    parser.add_argument("taxi_type", choices=("yellow", "green"))
    parser.add_argument("year", type=int)
    parser.add_argument("month", type=int)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    batch = Batch(args.taxi_type, args.year, args.month)
    result = ingest_batch(batch)

    if result.is_loaded:
        print(f"Loaded {result.row_count:,} rows into DuckDB.")
    else:
        print("Batch has issues:")
        for error in result.errors:
            print(f"- {error}")

    if result.warnings:
        print("Warnings:")
        for warning in result.warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
