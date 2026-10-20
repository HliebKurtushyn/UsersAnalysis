import pandas as pd

from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

ENGAGEMENT_FEATURE_COLUMNS = ["views", "carts"]


def create_model(cv: int = 3):
    """Create a small baseline classifier for further tuning."""
    return GridSearchCV(
        RandomForestClassifier(
            class_weight="balanced",
            random_state=42,
        ),
        param_grid={"n_estimators": [100]},
        cv=cv,
    )


def _cross_validation_splits(target: pd.Series, maximum: int = 3) -> int:
    """Choose a valid CV split count for the smallest target class."""
    smallest_class = target.value_counts().min()
    return max(2, min(maximum, int(smallest_class)))


def build_engagement_target(
    features: pd.DataFrame,
) -> pd.Series:
    """Label users who completed at least one purchase."""
    return (features["purchases"] >= 1).astype(int)


def split_data(
    features: pd.DataFrame, test_size: float = 0.2, random_state: int = 42
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split user features and target into training and test sets."""

    y = build_engagement_target(features)
    X = features[ENGAGEMENT_FEATURE_COLUMNS]

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

    model = create_model(cv=_cross_validation_splits(y_train))
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    y_score = model.predict_proba(X_test)[:, 1]

    return {
        "accuracy": accuracy_score(y_test, y_pred),
        "balanced_accuracy": (
            balanced_accuracy_score(y_test, y_pred) if y_test.nunique() > 1 else 0.0
        ),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0),
        "average_precision": average_precision_score(y_test, y_score),
        "roc_auc": (roc_auc_score(y_test, y_score) if y_test.nunique() > 1 else 0.0),
    }


def check_class_balance(target: pd.Series) -> dict[str, pd.Series]:
    """Check the balance of classes in the target variable and return the counts and ratios."""
    class_counts = target.value_counts()
    class_ratios = target.value_counts(normalize=True)

    return {"class_counts": class_counts, "class_ratios": class_ratios}
