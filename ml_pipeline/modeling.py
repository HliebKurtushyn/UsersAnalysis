from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV


def create_model():
    """Create a small baseline classifier for further tuning."""
    return GridSearchCV(
        RandomForestClassifier(random_state=42),
        param_grid={"n_estimators": [100]},
        cv=3,
    )
