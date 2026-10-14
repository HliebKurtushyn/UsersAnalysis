import pandas as pd


EVENT_FEATURES = {
    "view": "views",
    "cart": "carts",
    "purchase": "purchases",
}


def build_user_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build one feature row for every user."""
    required_columns = {"user_id", "event_type"}

    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    events = data[data["event_type"].isin(EVENT_FEATURES)].copy()

    events["feature"] = events["event_type"].map(EVENT_FEATURES)
    events["value"] = 1

    features = events.pivot_table(
        index="user_id",
        columns="feature",
        values="value",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for column in ("views", "carts", "purchases"):
        if column not in features:
            features[column] = 0

    return features[["user_id", "views", "carts", "purchases"]]
