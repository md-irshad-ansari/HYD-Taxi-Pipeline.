from pathlib import Path
import requests
from ingestion.batch import (
    CHUNK_SIZE,
    REQUEST_TIMEOUT,
    Batch,
    get_raw_path,
    get_trip_url,
)

def download_batch(batch: Batch) -> Path:
    url = get_trip_url(batch)
    destination = get_raw_path(batch)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temp_path = destination.with_suffix(".parquet.part")
    try:
        response = requests.get(url, stream=True, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        with temp_path.open("wb") as output_file:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    output_file.write(chunk)
        temp_path.replace(destination)     
        return destination                  
    except Exception:
        if temp_path.exists():
            temp_path.unlink()
        raise





    
