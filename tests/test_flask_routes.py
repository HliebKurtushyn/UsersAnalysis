from web_app.app import app
from web_app.app import client_queue, transaction_stack


def test_home_page():
    client = app.test_client()
    response = client.get("/")
    assert response.status_code == 200


def setup_function():
    client_queue.items.clear()
    transaction_stack.items.clear()


def test_enqueue_client():
    client = app.test_client()

    response = client.post("/api/queue", json={"value": "222"})

    assert response.status_code == 201
    assert response.get_json() == {"value": "222"}
    assert client_queue.items == ["222"]


def test_push_transaction():
    client = app.test_client()

    response = client.post("/api/transactions", json={"value": "222"})

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
