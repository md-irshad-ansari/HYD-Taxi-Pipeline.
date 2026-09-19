from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SEED_DIR = DATA_DIR / "seed"
WAREHOUSE_DIR = DATA_DIR / "warehouse"
EXPORT_DIR = DATA_DIR / "export"
DB_PATH = WAREHOUSE_DIR / "nyc_taxi.duckdb"

# Data sources
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
ZONE_LOOKUP_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"

# Network settings
CHUNK_SIZE = 1024 * 1024
REQUEST_TIMEOUT = 60


def get_trip_url(batch: Batch) -> str:
    return f"{BASE_URL}/{batch.taxi_type}_tripdata_{batch.year:04d}-{batch.month:02d}.parquet"


def get_raw_path(batch: Batch) -> Path:
    return RAW_DATA_DIR / f"{batch.taxi_type}/{batch.year:04d}/{batch.month:02d}.parquet"
    

class Batch:
    def __init__(self, taxi_type: str, year: int, month: int):
        if taxi_type not in ("yellow", "green"):
            raise ValueError("taxi_type must be 'yellow' or 'green'")
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")

        self.taxi_type = taxi_type
        self.year = year
        self.month = month

    @property
    # 1 batch <=> taxi_type_year_month
    def batch_id(self) -> str:
        return f"{self.taxi_type}/{self.year:04d}/{self.month:02d}"




    

    
