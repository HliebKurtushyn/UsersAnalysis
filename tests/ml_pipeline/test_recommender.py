import pandas as pd
import pytest

from ml_pipeline.recommender import top_products


def test_top_products_returns_products_by_purchase_to_view_ratio():
    products = pd.DataFrame(
        {
            "product_id": [101, 202, 303],
            "views": [100, 10, 0],
            "carts": [5, 2, 1],
            "purchases": [5, 2, 1],
        }
    )

    result = top_products(products, limit=2)

    assert result["product_id"].tolist() == [202, 101]
    assert result["purchases"].tolist() == [2, 5]
    assert "_purchase_to_view_ratio" not in result.columns


def test_top_products_assigns_zero_ratio_to_products_without_views():
    products = pd.DataFrame(
        {
            "product_id": [101, 202],
            "views": [0, 10],
            "purchases": [5, 1],
        }
    )

    result = top_products(products)

    assert result["product_id"].tolist() == [202, 101]


def test_top_products_preserves_order_for_equal_ratios_and_applies_limit():
    products = pd.DataFrame(
        {
            "product_id": [101, 202, 303],
            "views": [10, 20, 30],
            "purchases": [1, 2, 3],
        }
    )

    result = top_products(products, limit=2)

    assert result["product_id"].tolist() == [101, 202]


def test_top_products_does_not_modify_input():
    products = pd.DataFrame(
        {
            "product_id": [101],
            "views": [10],
            "purchases": [1],
        }
    )
    original = products.copy()

    top_products(products)

    pd.testing.assert_frame_equal(products, original)


def test_top_products_rejects_missing_required_columns():
    products = pd.DataFrame({"product_id": [101], "views": [10]})

    with pytest.raises(ValueError, match="purchases"):
        top_products(products)


def test_top_products_rejects_non_positive_limit():
    products = pd.DataFrame(
        {
            "product_id": [101],
            "views": [10],
            "purchases": [1],
        }
    )

    with pytest.raises(ValueError, match="limit"):
        top_products(products, limit=0)
