from pathlib import Path

import pandas as pd


def load_data(path: str | Path, rows: int | None = None) -> pd.DataFrame:
    """Load the source event log."""
    return pd.read_csv(path, nrows=rows)


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and fill the basic categorical fields."""
    cleaned = data.drop_duplicates().copy()
    for column in ("brand", "category_code"):
        if column in cleaned:
            cleaned[column] = cleaned[column].fillna("Unknown")
    return cleaned
