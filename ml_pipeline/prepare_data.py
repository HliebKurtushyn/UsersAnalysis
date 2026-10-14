from pathlib import Path

from ml_pipeline.data_loader import DEFAULT_DATA_PATH, load_data
from ml_pipeline.eda_and_cleaning import (
    DEFAULT_CLEANED_DATA_PATH,
    clean_data,
    save_cleaned_data,
)


def prepare_data(
    source_path: str | Path = DEFAULT_DATA_PATH,
    output_path: str | Path = DEFAULT_CLEANED_DATA_PATH,
    rows: int | None = None,
) -> Path:
    """Load raw data, clean it, and save the cleaned dataset."""
    raw_data = load_data(path=source_path, rows=rows)
    cleaned_data = clean_data(raw_data)
    return save_cleaned_data(cleaned_data, output_path)
