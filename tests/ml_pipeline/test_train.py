import importlib

import pandas as pd


train_module = importlib.import_module("ml_pipeline.train")


class FakeModel:
    def __init__(self):
        self.fit_calls = []

    def fit(self, X, y):
        self.fit_calls.append((X, y))
        return self


def test_train_runs_pipeline_and_saves_artifacts(monkeypatch, tmp_path):
    raw_data = pd.DataFrame({"event_type": ["view"]})
    cleaned_data = pd.DataFrame({"event_type": ["cleaned"]})
    user_features = pd.DataFrame(
        {
            "user_id": [1, 2],
            "views": [10, 20],
            "carts": [2, 4],
            "purchases": [1, 3],
        }
    )
    product_features = pd.DataFrame(
        {
            "product_id": [101, 202],
            "views": [10, 20],
            "carts": [2, 4],
            "purchases": [1, 3],
        }
    )
    user_clusters = pd.DataFrame({"user_id": [1, 2], "cluster": [0, 1]})
    product_clusters = pd.DataFrame({"product_id": [101, 202], "cluster": [0, 1]})
    X_train = user_features[["views", "carts"]].iloc[:1]
    X_test = user_features[["views", "carts"]].iloc[1:]
    y_train = pd.Series([0])
    y_test = pd.Series([1])
    model = FakeModel()
    dump_calls = []

    monkeypatch.setattr(train_module, "RAW_DATA_PATH", tmp_path / "raw.csv")
    monkeypatch.setattr(
        train_module,
        "CLEANED_DATA_PATH",
        tmp_path / "cleaned.csv",
    )
    monkeypatch.setattr(train_module, "ARTIFACTS_DIR", tmp_path / "artifacts")
    monkeypatch.setattr(
        train_module,
        "load_data",
        lambda path: raw_data,
    )
    monkeypatch.setattr(train_module, "clean_data", lambda data: cleaned_data)
    monkeypatch.setattr(
        train_module,
        "build_user_features",
        lambda data: user_features,
    )
    monkeypatch.setattr(
        train_module,
        "build_product_features",
        lambda data: product_features,
    )
    monkeypatch.setattr(
        train_module,
        "cluster_users",
        lambda ids, features, clusters: user_clusters,
    )
    monkeypatch.setattr(
        train_module,
        "cluster_products",
        lambda ids, features, clusters: product_clusters,
    )
    monkeypatch.setattr(
        train_module,
        "split_data",
        lambda features: (X_train, X_test, y_train, y_test),
    )
    monkeypatch.setattr(train_module, "create_model", lambda: model)
    monkeypatch.setattr(
        train_module,
        "build_engagement_target",
        lambda features: pd.Series([0, 1]),
    )
    monkeypatch.setattr(
        train_module.joblib,
        "dump",
        lambda value, path: dump_calls.append((value, path)),
    )

    result = train_module.train()

    assert result["user_features"].equals(user_features)
    assert result["product_features"].equals(product_features)
    assert result["user_clusters"].equals(user_clusters)
    assert result["product_clusters"].equals(product_clusters)
    assert len(model.fit_calls) == 1
    assert [path.name for _, path in dump_calls] == [
        "engagement_model.joblib",
        "user_features.joblib",
        "product_features.joblib",
        "user_clusters.joblib",
        "product_clusters.joblib",
        "metadata.joblib",
    ]
    assert dump_calls[-1][0]["train_rows"] == 1
    assert dump_calls[-1][0]["test_rows"] == 1


def test_train_prefers_existing_cleaned_data(monkeypatch, tmp_path):
    cleaned_path = tmp_path / "cleaned.csv"
    cleaned_path.touch()
    raw_path = tmp_path / "raw.csv"
    loaded_paths = []

    monkeypatch.setattr(train_module, "CLEANED_DATA_PATH", cleaned_path)
    monkeypatch.setattr(train_module, "RAW_DATA_PATH", raw_path)
    monkeypatch.setattr(
        train_module,
        "load_data",
        lambda path: loaded_paths.append(path) or pd.DataFrame(),
    )
    monkeypatch.setattr(
        train_module,
        "clean_data",
        lambda data: pd.DataFrame(),
    )
    monkeypatch.setattr(
        train_module,
        "build_user_features",
        lambda data: pd.DataFrame(
            {
                "user_id": [1],
                "views": [1],
                "carts": [0],
                "purchases": [0],
            }
        ),
    )
    monkeypatch.setattr(
        train_module,
        "build_product_features",
        lambda data: pd.DataFrame(
            {
                "product_id": [101],
                "views": [1],
                "carts": [0],
                "purchases": [0],
            }
        ),
    )
    monkeypatch.setattr(
        train_module,
        "cluster_users",
        lambda ids, features, clusters: pd.DataFrame(),
    )
    monkeypatch.setattr(
        train_module,
        "cluster_products",
        lambda ids, features, clusters: pd.DataFrame(),
    )
    monkeypatch.setattr(
        train_module,
        "split_data",
        lambda features: (
            pd.DataFrame({"views": [1], "carts": [0]}),
            pd.DataFrame(),
            pd.Series([0]),
            pd.Series(dtype=int),
        ),
    )
    monkeypatch.setattr(train_module, "create_model", lambda: FakeModel())
    monkeypatch.setattr(
        train_module,
        "build_engagement_target",
        lambda features: pd.Series([0]),
    )
    monkeypatch.setattr(train_module.joblib, "dump", lambda value, path: None)

    train_module.train()

    assert loaded_paths == [cleaned_path]
