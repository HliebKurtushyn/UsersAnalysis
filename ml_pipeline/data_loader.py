from pathlib import Path

import pandas as pd


DEFAULT_DATA_PATH = Path("data/raw/2019-Nov.csv")
DEFAULT_CLEANED_DATA_PATH = Path("data/cleaned/2019-Nov.csv")

REQUIRED_COLUMNS = {
    "event_type",
    "user_id",
    "event_time",
    "product_id",
    "category_code",
    "brand",
    "price",
}


def load_data(
    path: str | Path | None = None,
    rows: int | None = None,
    cleaned_path: str | Path = DEFAULT_CLEANED_DATA_PATH,
) -> pd.DataFrame:
    """Load validated event data, preferring the cleaned default dataset."""
    source_path = Path(path) if path is not None else DEFAULT_DATA_PATH
    cache_path = Path(cleaned_path)

    if path is None and cache_path.exists():
        source_path = cache_path

    df = pd.read_csv(source_path, nrows=rows)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(f"CSV is missing required columns: {sorted(missing_columns)}")

    return df
