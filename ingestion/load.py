from pathlib import Path
import duckdb
from ingestion.batch import DB_PATH, Batch
from ingestion.validate import get_required_types


RAW_TABLE_NAMES = {
    "yellow": "raw_yellow_trips",
    "green": "raw_green_trips",
}


def load_raw_batch(
    batch: Batch,
    raw_path: Path,
    db_path: Path = DB_PATH,
) -> int:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    table_name = RAW_TABLE_NAMES[batch.taxi_type]
    contract_names = get_required_types(batch)
    column_names = ", ".join(f'"{name}"' for name in contract_names)

    connection = duckdb.connect(str(db_path))
    try:
        connection.begin()

        connection.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {table_name} AS
            SELECT
                {column_names},
                CAST(? AS INTEGER) AS batch_year,
                CAST(? AS INTEGER) AS batch_month
            FROM read_parquet(?)
            
            WHERE FALSE
            """,
            [batch.year, batch.month, str(raw_path)],
        )

        connection.execute(
            f"""
            DELETE FROM {table_name}
            WHERE batch_year = ? AND batch_month = ?
            """,
            [batch.year, batch.month],
        )

        row_count = connection.execute(
            "SELECT count(*) FROM read_parquet(?)",
            [str(raw_path)],
        ).fetchone()[0]

        connection.execute(
            f"""
            INSERT INTO {table_name} BY NAME
            SELECT
                {column_names},
                CAST(? AS INTEGER) AS batch_year,
                CAST(? AS INTEGER) AS batch_month
            FROM read_parquet(?)
            """,
            [batch.year, batch.month, str(raw_path)],
        )

        connection.commit()
        return row_count
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

