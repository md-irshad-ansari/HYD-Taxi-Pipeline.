from pathlib import Path
import polars as pl
from ingestion.batch import Batch


class ValidationResult:
    """Result of validating one downloaded raw Parquet file."""

    def __init__(self, errors=(), warnings=()):
        self.errors = tuple(errors)
        self.warnings = tuple(warnings)

    @property
    def is_valid(self) -> bool:
        return not self.errors


COMMON_REQUIRED_TYPES = {
    "VendorID": "integer",
    "passenger_count": "integer",
    "trip_distance": "numeric",
    "RatecodeID": "integer",
    "store_and_fwd_flag": "string",
    "PULocationID": "integer",
    "DOLocationID": "integer",
    "payment_type": "integer",
    "fare_amount": "numeric",
    "extra": "numeric",
    "mta_tax": "numeric",
    "tip_amount": "numeric",
    "tolls_amount": "numeric",
    "improvement_surcharge": "numeric",
    "total_amount": "numeric",
}

YELLOW_REQUIRED_TYPES = {
    "tpep_pickup_datetime": "datetime",
    "tpep_dropoff_datetime": "datetime",
    "congestion_surcharge": "numeric",
    "Airport_fee": "numeric",
}

GREEN_REQUIRED_TYPES = {
    "lpep_pickup_datetime": "datetime",
    "lpep_dropoff_datetime": "datetime",
    "trip_type": "integer",
    "congestion_surcharge": "numeric",
}


def get_required_types(batch: Batch) -> dict[str, str]:
    if batch.taxi_type == "yellow":
        taxi_types = YELLOW_REQUIRED_TYPES
    else:
        taxi_types = GREEN_REQUIRED_TYPES

    required_types = {**COMMON_REQUIRED_TYPES, **taxi_types}
    if batch.year >= 2025:
        required_types["cbd_congestion_fee"] = "numeric"

    return required_types


def is_correct_type(dtype: pl.DataType, expected: str) -> bool:
    if expected == "integer":
        return dtype.is_integer()
    if expected == "numeric":
        return dtype.is_numeric()
    if expected == "datetime":
        return dtype == pl.Datetime
    if expected == "string":
        return dtype == pl.String
    raise ValueError(f"Unknown expected type: {expected}")


def validate_raw_file(batch: Batch, path: Path) -> ValidationResult:
    """Validate the file-level contract for one taxi batch."""

    if not path.exists():
        return ValidationResult(errors=(f"File does not exist: {path}",))
    if not path.is_file():
        return ValidationResult(errors=(f"Path is not a file: {path}",))
    if path.stat().st_size == 0:
        return ValidationResult(errors=("File is empty",))

    try:
        schema = pl.read_parquet_schema(path)
    except Exception as exc:
        return ValidationResult(errors=(f"Unable to read Parquet: {exc}",))

    expected = get_required_types(batch)
    actual_names = set(schema)
    expected_names = set(expected)
    required_names = set(expected)

    errors: list[str] = []
    warnings: list[str] = []

    missing_names = sorted(required_names - actual_names)
    if missing_names:
        errors.append(f"Missing columns: {missing_names}")

    extra_names = sorted(actual_names - expected_names)
    if extra_names:
        warnings.append(f"Extra columns present: {extra_names}")

    for name, expected_type in expected.items():
        if name not in schema:
            continue
        actual_type = schema[name]
        if not is_correct_type(actual_type, expected_type):
            errors.append(
                f"Invalid type for {name}: expected {expected_type}, got {actual_type}"
            )

    return ValidationResult(tuple(errors), tuple(warnings))
