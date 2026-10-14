import pandas as pd
import pytest

import ml_pipeline.clustering as clustering_module
from ml_pipeline.clustering import cluster_users, find_optimal_clusters


@pytest.fixture
def user_features():
    return pd.DataFrame(
        {
            "views": [1, 2, 10, 11],
            "carts": [0, 1, 5, 6],
            "purchases": [0, 0, 2, 3],
        }
    )


def test_find_optimal_clusters_plots_inertia_for_candidate_counts(
    user_features,
    monkeypatch,
):
    plot_calls = []
    show_calls = []

    monkeypatch.setattr(
        clustering_module.plt,
        "plot",
        lambda k_values, inertias, marker: plot_calls.append(
            (list(k_values), inertias, marker)
        ),
    )
    monkeypatch.setattr(
        clustering_module.plt,
        "show",
        lambda: show_calls.append(True),
    )

    result = find_optimal_clusters(user_features, max_clusters=3)

    assert result is None
    assert len(plot_calls) == 1
    assert plot_calls[0][0] == [1, 2, 3]
    assert len(plot_calls[0][1]) == 3
    assert all(inertia >= 0 for inertia in plot_calls[0][1])
    assert plot_calls[0][2] == "o"
    assert show_calls == [True]


def test_find_optimal_clusters_does_not_use_more_clusters_than_rows(
    user_features,
    monkeypatch,
):
    plot_calls = []
    monkeypatch.setattr(
        clustering_module.plt,
        "plot",
        lambda k_values, inertias, marker: plot_calls.append(
            (list(k_values), inertias, marker)
        ),
    )
    monkeypatch.setattr(clustering_module.plt, "show", lambda: None)

    find_optimal_clusters(user_features.iloc[:2], max_clusters=10)

    assert plot_calls[0][0] == [1, 2]
    assert len(plot_calls[0][1]) == 2


def test_find_optimal_clusters_rejects_empty_features(monkeypatch):
    monkeypatch.setattr(clustering_module.plt, "show", lambda: None)

    with pytest.raises(ValueError, match="must not be empty"):
        find_optimal_clusters(pd.DataFrame(), max_clusters=3)


def test_find_optimal_clusters_rejects_invalid_max_clusters():
    features = pd.DataFrame({"views": [1, 2]})

    with pytest.raises(ValueError, match="at least 1"):
        find_optimal_clusters(features, max_clusters=0)


def test_cluster_users_returns_user_ids_and_labels():
    user_ids = pd.Series([101, 202, 303, 404])
    features = pd.DataFrame(
        {
            "views": [1, 2, 10, 11],
            "carts": [0, 1, 5, 6],
            "purchases": [0, 0, 2, 3],
        }
    )

    result = cluster_users(user_ids, features, clusters=2)

    assert result.columns.tolist() == ["user_id", "cluster"]
    assert result["user_id"].tolist() == [101, 202, 303, 404]
    assert len(result["cluster"].unique()) == 2
    assert len(result) == len(user_ids)


def test_cluster_users_rejects_empty_features():
    with pytest.raises(ValueError, match="must not be empty"):
        cluster_users(pd.Series(dtype=int), pd.DataFrame(), clusters=1)


def test_cluster_users_rejects_mismatched_input_lengths():
    with pytest.raises(ValueError, match="same length"):
        cluster_users(
            pd.Series([101]),
            pd.DataFrame({"views": [1, 2]}),
            clusters=1,
        )


@pytest.mark.parametrize("clusters", [0, 5])
def test_cluster_users_rejects_invalid_cluster_count(clusters, user_features):
    with pytest.raises(
        ValueError,
        match="between 1 and the number of users",
    ):
        cluster_users(
            pd.Series([101, 202, 303, 404]),
            user_features,
            clusters=clusters,
        )
