import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
)


def create_model():
    """Create a small baseline classifier for further tuning."""
    return GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid={"n_estimators": [100]},
        cv=3,
    )


def build_engagement_target(
    features: pd.DataFrame,
) -> pd.Series:
    """Label users with at least 3 purchases as highly engaged."""
    return (features["purchases"] >= 3).astype(int)


def split_data(
    features: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split user features and target into training and test sets."""

    y = build_engagement_target(features)
    X = features[["views", "carts"]]

    return train_test_split(
        X,
        y,
        test_size=test_size,
        random_state=random_state,
        stratify=y,
    )


def evaluate_model(features: pd.DataFrame) -> dict[str, float]:
    """Evaluate the model on the test set and return metrics."""
    X_train, X_test, y_train, y_test = split_data(features)

    model = create_model()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred),
        "f1": f1_score(y_test, y_pred),
    }
