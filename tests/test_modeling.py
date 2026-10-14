import pandas as pd
import pytest
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

from ml_pipeline.modeling import (
    build_engagement_target,
    check_class_balance,
    create_model,
    evaluate_model,
    split_data,
)


@pytest.fixture
def engagement_features():
    return pd.DataFrame(
        {
            "views": [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
            ],
            "carts": [
                0,
                0,
                1,
                1,
                2,
                2,
                3,
                3,
                4,
                4,
            ],
            "purchases": [
                0,
                1,
                2,
                3,
                4,
                0,
                1,
                2,
                3,
                5,
            ],
        }
    )


def test_create_model_returns_grid_search_with_random_forest():
    model = create_model()

    assert isinstance(model, GridSearchCV)
    assert isinstance(model.estimator, RandomForestClassifier)
    assert model.param_grid == {"n_estimators": [100]}
    assert model.cv == 3


def test_build_engagement_target_marks_users_with_at_least_three_purchases(
    engagement_features,
):
    result = build_engagement_target(engagement_features)

    assert result.tolist() == [0, 0, 0, 1, 1, 0, 0, 0, 1, 1]
    assert result.dtype == "int64"


def test_split_data_returns_features_and_target_with_expected_shapes(
    engagement_features,
):
    X_train, X_test, y_train, y_test = split_data(
        engagement_features,
        test_size=0.2,
        random_state=42,
    )

    assert list(X_train.columns) == ["views", "carts"]
    assert list(X_test.columns) == ["views", "carts"]
    assert len(X_train) == 8
    assert len(X_test) == 2
    assert len(y_train) == 8
    assert len(y_test) == 2
    assert set(y_train.unique()) == {0, 1}
    assert set(y_test.unique()) == {0, 1}


def test_check_class_balance_returns_counts_and_ratios():
    target = pd.Series([0, 0, 0, 1, 1])

    result = check_class_balance(target)

    assert result["class_counts"].to_dict() == {0: 3, 1: 2}
    assert result["class_ratios"].to_dict() == {
        0: pytest.approx(0.6),
        1: pytest.approx(0.4),
    }
    assert result["class_ratios"].sum() == pytest.approx(1.0)


def test_evaluate_model_returns_required_metrics(engagement_features):
    result = evaluate_model(engagement_features)

    assert set(result) == {"accuracy", "precision", "recall", "f1"}

    for metric_value in result.values():
        assert 0.0 <= metric_value <= 1.0
