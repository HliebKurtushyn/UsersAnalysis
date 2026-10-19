from web_app.app import OperationLog, app, client_queue, db, transaction_stack
import joblib
import pandas as pd


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"v0.7.1" in response.data


def test_sidebar_pages_render_with_active_navigation():
    client = app.test_client()

    pages = {
        "/queue": b"Queue",
        "/transactions": b"Transactions",
        "/logs": b"Operation Log",
        "/analytics": b"Analytics",
        "/products": b"ML / Products",
        "/users": b"ML / Users",
    }

    for path, expected_title in pages.items():
        response = client.get(path)

        assert response.status_code == 200
        assert expected_title in response.data
        assert b"href=" in response.data


def test_analytics_page_shows_operation_counts():
    client = app.test_client()
    client.post(
        "/api/queue",
        json={"user_id": "user-1", "value": "client-1"},
    )

    response = client.get("/analytics")

    assert response.status_code == 200
    assert "Усього операцій".encode() in response.data
    assert b"1" in response.data


def test_products_page_sorts_features(monkeypatch, tmp_path):
    features = pd.DataFrame(
        {
            "product_id": [101, 202],
            "views": [30, 10],
            "carts": [3, 1],
            "purchases": [2, 5],
        }
    )
    clusters = pd.DataFrame({"product_id": [101, 202], "cluster": [0, 1]})
    joblib.dump(features, tmp_path / "product_features.joblib")
    joblib.dump(clusters, tmp_path / "product_clusters.joblib")
    monkeypatch.setattr("web_app.app.ARTIFACTS_DIR", tmp_path)

    response = app.test_client().get("/products?sort_by=purchases&order=desc")

    assert response.status_code == 200
    assert response.data.index(b">202<") < response.data.index(b">101<")


def test_users_page_merges_features_and_clusters(monkeypatch, tmp_path):
    features = pd.DataFrame(
        {
            "user_id": [1],
            "views": [10],
            "carts": [2],
            "purchases": [3],
        }
    )
    clusters = pd.DataFrame({"user_id": [1], "cluster": [2]})
    joblib.dump(features, tmp_path / "user_features.joblib")
    joblib.dump(clusters, tmp_path / "user_clusters.joblib")
    monkeypatch.setattr("web_app.app.ARTIFACTS_DIR", tmp_path)

    response = app.test_client().get("/users")

    assert response.status_code == 200
    assert b"ML / Users" in response.data
    assert b">2<" in response.data


def test_ml_overview_and_recommendations_render_without_artifacts(
    monkeypatch, tmp_path
):
    monkeypatch.setattr("web_app.app.ARTIFACTS_DIR", tmp_path)
    client = app.test_client()

    overview = client.get("/ml")
    recommendations = client.get("/recommendations")

    assert overview.status_code == 200
    assert b"ML Overview" in overview.data
    assert b"Missing" in overview.data
    assert recommendations.status_code == 200
    assert "Product features недоступні".encode() in recommendations.data


def test_train_ml_pipeline_endpoint(monkeypatch):
    calls = []
    monkeypatch.setattr("web_app.app.train", lambda: calls.append(True))

    response = app.test_client().post("/api/ml/train")

    assert response.status_code == 200
    assert response.get_json() == {
        "message": "ML artifacts were recreated successfully."
    }
    assert calls == [True]


def test_prepare_ml_dataset_endpoint(monkeypatch, tmp_path):
    calls = []
    output_path = tmp_path / "cleaned.csv"

    def fake_prepare_data(**kwargs):
        calls.append(kwargs)
        return output_path

    monkeypatch.setattr("web_app.app.prepare_data", fake_prepare_data)
    monkeypatch.setattr("web_app.app.RAW_DATA_PATH", tmp_path / "raw.csv")
    monkeypatch.setattr("web_app.app.CLEANED_DATA_PATH", output_path)

    response = app.test_client().post(
        "/api/ml/prepare-data",
        json={"rows": 5000},
    )

    assert response.status_code == 200
    assert response.get_json()["rows"] == 5000
    assert calls == [
        {
            "source_path": tmp_path / "raw.csv",
            "output_path": output_path,
            "rows": 5000,
        }
    ]


def setup_function():
    client_queue.items.clear()
    transaction_stack.items.clear()
    with app.app_context():
        db.session.query(OperationLog).delete()
        db.session.commit()


def test_enqueue_client():
    client = app.test_client()

    response = client.post(
        "/api/queue",
        json={"user_id": "user-1", "value": "222"},
    )

    assert response.status_code == 201
    assert response.get_json() == {"value": "222"}
    assert client_queue.items == ["222"]


def test_push_transaction():
    client = app.test_client()

    response = client.post(
        "/api/transactions",
        json={"user_id": "user-1", "value": "222"},
    )

    assert response.status_code == 201
    assert response.get_json() == {"value": "222"}
    assert transaction_stack.items == ["222"]


def test_api_rejects_missing_json_content_type():
    client = app.test_client()

    response = client.post("/api/queue", data='{"value": "222"}')

    assert response.status_code == 415
    assert response.get_json()["error"] == "Content-Type must be application/json"


def test_api_rejects_invalid_payload():
    client = app.test_client()

    response = client.post("/api/queue", json={"value": ""})

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid request"
    assert client_queue.items == []


def test_api_rejects_json_string_payload():
    client = app.test_client()

    response = client.post("/api/queue", json="222")

    assert response.status_code == 400
    assert response.get_json()["error"] == "Invalid request"


def test_get_queue_returns_all_items_without_limit():
    client = app.test_client()
    client_queue.items.extend(["first", "second", "third"])

    response = client.get("/api/queue")

    assert response.status_code == 200
    assert response.get_json() == {
        "items": ["first", "second", "third"],
    }


def test_get_queue_applies_positive_limit():
    client = app.test_client()
    client_queue.items.extend(["first", "second", "third"])

    response = client.get("/api/queue?limit=2")

    assert response.status_code == 200
    assert response.get_json() == {"items": ["first", "second"]}


def test_get_queue_limit_larger_than_queue_returns_all_items():
    client = app.test_client()
    client_queue.items.extend(["first", "second"])

    response = client.get("/api/queue?limit=10")

    assert response.status_code == 200
    assert response.get_json() == {"items": ["first", "second"]}


def test_get_queue_rejects_invalid_limit():
    client = app.test_client()

    for invalid_limit in ("0", "-1", "abc"):
        response = client.get(f"/api/queue?limit={invalid_limit}")

        assert response.status_code == 400
        assert response.get_json()["error"] == "Invalid query parameters"


def test_get_operation_logs_returns_newest_logs_first():
    client = app.test_client()

    first = client.post(
        "/api/queue",
        json={"user_id": "user-1", "value": "first"},
    )
    second = client.post(
        "/api/transactions",
        json={"user_id": "user-2", "value": "second"},
    )

    assert first.status_code == 201
    assert second.status_code == 201

    response = client.get("/api/logs")

    assert response.status_code == 200
    logs = response.get_json()["items"]
    assert len(logs) == 2
    assert logs[0]["value"] == "second"
    assert logs[0]["structure"] == "stack"
    assert logs[1]["value"] == "first"
    assert logs[1]["structure"] == "queue"


def test_dequeue_returns_and_logs_actual_queue_value():
    client = app.test_client()
    client_queue.enqueue("actual-client")

    response = client.delete(
        "/api/queue/dequeue",
        json={"user_id": "user-1"},
    )

    assert response.status_code == 200
    assert response.get_json() == {"value": "actual-client"}

    with app.app_context():
        log = OperationLog.query.one()
        assert log.value == "actual-client"
        assert log.operation_type == "dequeue"


def test_pop_returns_not_found_for_empty_stack():
    client = app.test_client()

    response = client.delete(
        "/api/transactions/pop",
        json={"user_id": "user-1"},
    )

    assert response.status_code == 404
    assert response.get_json() == {"error": "Stack is empty"}
