from pathlib import Path

import pandas as pd


DEFAULT_CLEANED_DATA_PATH = Path("data/cleaned/2019-Nov.csv")


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and handle missing values."""
    cleaned = data.drop_duplicates().copy()

    if "event_time" in cleaned.columns:
        cleaned["event_time"] = pd.to_datetime(
            cleaned["event_time"],
            errors="coerce",
        )

    for column in ("brand", "category_code"):
        if column in cleaned.columns:
            cleaned[column] = cleaned[column].fillna("Unknown")

    required_columns = [
        column
        for column in ("user_id", "product_id", "price", "event_type")
        if column in cleaned.columns
    ]
    cleaned = cleaned.dropna(subset=required_columns)

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
