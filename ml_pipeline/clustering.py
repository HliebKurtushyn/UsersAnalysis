import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def find_optimal_clusters(
    features: pd.DataFrame,
    max_clusters: int = 10,
) -> None:
    """
    Plot inertia for different numbers of clusters using the Elbow Method.

    This function is intended for visualization and does not return a value.
    """
    if features.empty:
        raise ValueError("Features must not be empty.")

    if max_clusters < 1:
        raise ValueError("max_clusters must be at least 1.")

    scaled_features = StandardScaler().fit_transform(features)

    max_k = min(max_clusters, len(features))
    k_values = range(1, max_k + 1)
    inertias = []

    for k in k_values:
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
        )
        model.fit(scaled_features)
        inertias.append(model.inertia_)

    plt.plot(list(k_values), inertias, marker="o")
    plt.xlabel("Number of clusters (K)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method")
    plt.xticks(list(k_values))
    plt.show()


def cluster_users(
    user_ids: pd.Series,
    features: pd.DataFrame,
    clusters: int = 4,
) -> pd.DataFrame:
    """Scale user features and assign users to KMeans clusters."""
    if features.empty:
        raise ValueError("Features must not be empty.")

    if len(user_ids) != len(features):
        raise ValueError("user_ids and features must have the same length.")

    if not 1 <= clusters <= len(features):
        raise ValueError("clusters must be between 1 and the number of users.")

    scaled_features = StandardScaler().fit_transform(features)

    labels = KMeans(
        n_clusters=clusters,
        random_state=42,
        n_init=10,
    ).fit_predict(scaled_features)

    return pd.DataFrame(
        {
            "user_id": user_ids.to_numpy(),
            "cluster": labels,
        }
    )
