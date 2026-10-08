def top_products(products, limit: int = 5):
    """Return products ordered by their purchase-to-view ratio."""
    return sorted(
        products,
        key=lambda product: product["purchases"] / max(product["views"], 1),
        reverse=True,
    )[:limit]
