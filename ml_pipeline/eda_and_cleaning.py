import pandas as pd


def clean_data(data: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicates and fill missing categorical values."""
    cleaned = data.drop_duplicates().copy()

    for column in ("brand", "category_code"):
        if column in cleaned:
            cleaned[column] = cleaned[column].fillna("Unknown")

    return cleaned


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
