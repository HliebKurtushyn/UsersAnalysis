"""
Цей файл використовується для експериментів, ручного тестування для наочного результату тощо.
"""

from ml_pipeline.clustering import find_optimal_clusters
from ml_pipeline.data_loader import load_data
from ml_pipeline.feature_engineering import build_user_features
from ml_pipeline.prepare_data import prepare_data


def main() -> None:
    prepare_data(rows=10000)
    data = load_data()
    user_features = build_user_features(data)
    features = user_features[["views", "carts", "purchases"]]
    print(find_optimal_clusters(features, max_clusters=10))


if __name__ == "__main__":
    main()
