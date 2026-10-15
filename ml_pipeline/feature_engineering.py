import pandas as pd


EVENT_FEATURES = {
    "view": "views",
    "cart": "carts",
    "purchase": "purchases",
}


def _build_entity_features(
    data: pd.DataFrame,
    entity_column: str,
) -> pd.DataFrame:
    """Build event-count features for a user or product identifier."""
    required_columns = {entity_column, "event_type"}

    missing_columns = required_columns - set(data.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    events = data[data["event_type"].isin(EVENT_FEATURES)].copy()

    events["feature"] = events["event_type"].map(EVENT_FEATURES)
    events["value"] = 1

    features = events.pivot_table(
        index=entity_column,
        columns="feature",
        values="value",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for column in ("views", "carts", "purchases"):
        if column not in features:
            features[column] = 0

    return features.reset_index()[[entity_column, "views", "carts", "purchases"]]


def build_user_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build one feature row for every user."""
    return _build_entity_features(data, "user_id")


def build_product_features(data: pd.DataFrame) -> pd.DataFrame:
    """Build one feature row for every product."""
    return _build_entity_features(data, "product_id")
