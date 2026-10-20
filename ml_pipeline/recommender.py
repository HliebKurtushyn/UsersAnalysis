import math

import pandas as pd


def top_products(products: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """Return products ordered by a volume-adjusted purchase-to-view score."""
    required_columns = {"product_id", "views", "purchases"}
    missing_columns = required_columns - set(products.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {sorted(missing_columns)}")

    if limit < 1:
        raise ValueError("limit must be at least 1.")

    ranked_products = products.copy()
    ranked_products["_purchase_to_view_ratio"] = (
        ranked_products["purchases"]
        .div(ranked_products["views"])
        .where(ranked_products["views"] > 0, 0)
    )
    ranked_products["_recommendation_score"] = ranked_products.apply(
        _wilson_lower_bound,
        axis=1,
    )

    return (
        ranked_products.sort_values(
            ["_recommendation_score", "_purchase_to_view_ratio", "views"],
            ascending=False,
            kind="mergesort",
        )
        .drop(columns=["_purchase_to_view_ratio", "_recommendation_score"])
        .head(limit)
        .reset_index(drop=True)
    )


def _wilson_lower_bound(product: pd.Series, confidence_z: float = 1.96) -> float:
    """Estimate conversion conservatively when the number of views is small."""
    views = max(float(product["views"]), 0)
    if views == 0:
        return 0.0

    purchases = min(max(float(product["purchases"]), 0), views)
    ratio = purchases / views
    denominator = 1 + confidence_z**2 / views
    margin = confidence_z * math.sqrt(
        ratio * (1 - ratio) / views + confidence_z**2 / (4 * views**2)
    )
    return (ratio + confidence_z**2 / (2 * views) - margin) / denominator
