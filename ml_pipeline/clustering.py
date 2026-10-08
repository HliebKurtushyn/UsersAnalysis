from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


def cluster_users(features, clusters: int = 3):
    """Scale user features and assign them to KMeans clusters."""
    scaled_features = StandardScaler().fit_transform(features)
    return KMeans(n_clusters=clusters, random_state=42, n_init=10).fit_predict(
        scaled_features
    )
