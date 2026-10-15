from pathlib import Path

import joblib

from ml_pipeline.clustering import cluster_products, cluster_users
from ml_pipeline.data_loader import load_data
from ml_pipeline.eda_and_cleaning import clean_data
from ml_pipeline.feature_engineering import (
    build_product_features,
    build_user_features,
)
from ml_pipeline.modeling import (
    build_engagement_target,
    create_model,
    split_data,
)


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DATA_PATH = BASE_DIR / "data" / "raw" / "2019-Nov.csv"
CLEANED_DATA_PATH = BASE_DIR / "data" / "cleaned" / "2019-Nov.csv"
ARTIFACTS_DIR = BASE_DIR / "artifacts"


def _cluster_count(row_count: int, default: int = 4) -> int:
    """Use at most four clusters and never more than the number of rows."""
    return min(default, row_count)


def train() -> dict[str, object]:
    """Run the complete pipeline and save its artifacts."""
    source_path = CLEANED_DATA_PATH if CLEANED_DATA_PATH.exists() else RAW_DATA_PATH
    data = clean_data(load_data(path=source_path))

    user_features = build_user_features(data)
    product_features = build_product_features(data)

    user_feature_columns = ["views", "carts", "purchases"]
    product_feature_columns = ["views", "carts", "purchases"]

    user_clusters = cluster_users(
        user_features["user_id"],
        user_features[user_feature_columns],
        clusters=_cluster_count(len(user_features)),
    )
    product_clusters = cluster_products(
        product_features["product_id"],
        product_features[product_feature_columns],
        clusters=_cluster_count(len(product_features)),
    )

    X_train, X_test, y_train, y_test = split_data(user_features)
    model = create_model()
    model.fit(X_train, y_train)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, ARTIFACTS_DIR / "engagement_model.joblib")
    joblib.dump(user_features, ARTIFACTS_DIR / "user_features.joblib")
    joblib.dump(product_features, ARTIFACTS_DIR / "product_features.joblib")
    joblib.dump(user_clusters, ARTIFACTS_DIR / "user_clusters.joblib")
    joblib.dump(product_clusters, ARTIFACTS_DIR / "product_clusters.joblib")
    joblib.dump(
        {
            "user_feature_columns": user_feature_columns,
            "product_feature_columns": product_feature_columns,
            "target_definition": "purchases >= 3",
            "target": build_engagement_target(user_features),
            "test_rows": len(X_test),
            "train_rows": len(X_train),
            "test_target": y_test,
        },
        ARTIFACTS_DIR / "metadata.joblib",
    )

    return {
        "model": model,
        "user_features": user_features,
        "product_features": product_features,
        "user_clusters": user_clusters,
        "product_clusters": product_clusters,
    }


if __name__ == "__main__":
    train()
