import pandas as pd


def top_products(products: pd.DataFrame, limit: int = 5) -> pd.DataFrame:
    """Return products ordered by their purchase-to-view ratio."""
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

    return (
        ranked_products.sort_values(
            "_purchase_to_view_ratio",
            ascending=False,
        )
        .drop(columns="_purchase_to_view_ratio")
        .head(limit)
        .reset_index(drop=True)
    )
