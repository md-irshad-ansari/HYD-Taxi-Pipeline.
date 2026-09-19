from pathlib import Path

from ingestion.batch import Batch
from ingestion.download import download_batch
from ingestion.load import load_raw_batch
from ingestion.validate import validate_raw_file


class IngestionResult:
    """Observable result of attempting to ingest one Batch."""

    def __init__(
        self,
        batch: Batch,
        raw_path: Path,
        row_count: int | None = None,
        errors=(),
        warnings=(),
    ):
        self.batch = batch
        self.raw_path = raw_path
        self.row_count = row_count
        self.errors = tuple(errors)
        self.warnings = tuple(warnings)

    @property
    def is_loaded(self) -> bool:
        """Return True only when the Batch was loaded into DuckDB."""

        return self.row_count is not None and not self.errors


def ingest_batch(batch: Batch) -> IngestionResult:
    """Download, validate, and load one Batch in the required order.

    A Raw Source File that violates its Schema Contract is returned as an
    IngestionResult with errors and is not loaded. Network, filesystem, and
    DuckDB failures are allowed to propagate to the caller.
    """

    raw_path = download_batch(batch)
    validation = validate_raw_file(batch, raw_path)

    if not validation.is_valid:
        return IngestionResult(
            batch=batch,
            raw_path=raw_path,
            errors=validation.errors,
            warnings=validation.warnings,
        )

    row_count = load_raw_batch(batch, raw_path)

    return IngestionResult(
        batch=batch,
        raw_path=raw_path,
        row_count=row_count,
        warnings=validation.warnings,
    )
