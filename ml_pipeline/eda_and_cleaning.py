from pathlib import Path

import pandas as pd


DEFAULT_CLEANED_DATA_PATH = Path("data/cleaned/2019-Nov.csv")


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and fill missing categorical values."""
    cleaned = data.drop_duplicates().copy()

    for column in ("brand", "category_code"):
        if column in cleaned:
            cleaned[column] = cleaned[column].fillna("Unknown")

    return cleaned


def save_cleaned_data(
    data: pd.DataFrame,
    path: str | Path = DEFAULT_CLEANED_DATA_PATH,
) -> Path:
    """Save cleaned event data and create its parent directory if needed."""
    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)
    return output_path


def summarize_events(data: pd.DataFrame) -> pd.DataFrame:
    """Return event counts and percentages for exploratory analysis."""
    counts = data["event_type"].value_counts()
    percentages = data["event_type"].value_counts(normalize=True).mul(100)

    return pd.DataFrame(
        {
            "count": counts,
            "percentage": percentages,
        }
    )
