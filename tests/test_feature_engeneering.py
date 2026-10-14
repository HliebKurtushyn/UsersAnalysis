import pandas as pd
import pytest

from ml_pipeline.feature_engeneering import build_user_features


def test_build_user_features_aggregates_events_by_user():
    data = pd.DataFrame(
        {
            "user_id": [101, 101, 101, 202, 202],
            "event_type": ["view", "view", "purchase", "view", "cart"],
        }
    )

    result = build_user_features(data)

    result_by_user = result.set_index("user_id")

    assert list(result.columns) == [
        "user_id",
        "views",
        "carts",
        "purchases",
    ]
    assert result_by_user.loc[101, "views"] == 2
    assert result_by_user.loc[101, "carts"] == 0
    assert result_by_user.loc[101, "purchases"] == 1
    assert result_by_user.loc[202, "views"] == 1
    assert result_by_user.loc[202, "carts"] == 1
    assert result_by_user.loc[202, "purchases"] == 0


def test_build_user_features_ignores_unknown_event_types():
    data = pd.DataFrame(
        {
            "user_id": [101, 101, 202],
            "event_type": ["view", "remove_from_cart", "purchase"],
        }
    )

    result = build_user_features(data).set_index("user_id")

    assert result.loc[101, "views"] == 1
    assert result.loc[101, "carts"] == 0
    assert result.loc[101, "purchases"] == 0
    assert result.loc[202, "purchases"] == 1


def test_build_user_features_rejects_missing_required_columns():
    data = pd.DataFrame({"event_type": ["view"]})

    with pytest.raises(ValueError, match="user_id"):
        build_user_features(data)
