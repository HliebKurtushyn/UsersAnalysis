from pathlib import Path

import pandas as pd


DEFAULT_DATA_PATH = Path("data/raw/2019-Nov.csv")

REQUIRED_COLUMNS = {
    "event_type",
    "user_id",
    "event_time",
    "product_id",
    "category_code",
    "brand",
    "price"
}


def load_data(
    path: str | Path = DEFAULT_DATA_PATH,
    rows: int | None = None,
) -> pd.DataFrame:
    """Load the raw event log without modifying it."""
    df = pd.read_csv(path, nrows=rows)

    missing_columns = REQUIRED_COLUMNS - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"CSV is missing required columns: {sorted(missing_columns)}"
        )

    return df