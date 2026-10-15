from http import HTTPStatus

from flask import request

from web_app.app import app
from web_app.schemas import QueueRequest
from web_app.utils import validate_json_request


def test_validate_json_request_returns_validated_payload():
    with app.test_request_context(
        "/api/queue",
        method="POST",
        json={"user_id": "user-1", "value": "222"},
    ):
        result = validate_json_request(request, QueueRequest)

    assert isinstance(result, QueueRequest)
    assert result.value == "222"


def test_validate_json_request_rejects_non_json_request():
    with app.test_request_context(
        "/api/queue",
        method="POST",
        data='{"value": "222"}',
    ):
        result = validate_json_request(request, QueueRequest)

    response, status_code = result

    assert status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE
    assert response.get_json() == {"error": "Content-Type must be application/json"}


def test_validate_json_request_rejects_invalid_payload():
    with app.test_request_context(
        "/api/queue",
        method="POST",
        json={"value": ""},
    ):
        result = validate_json_request(request, QueueRequest)

    response, status_code = result

    assert status_code == HTTPStatus.BAD_REQUEST
    body = response.get_json()
    assert body["error"] == "Invalid request"
    assert body["details"]


def test_validate_json_request_rejects_extra_fields():
    with app.test_request_context(
        "/api/queue",
        method="POST",
        json={"value": "222", "unexpected": True},
    ):
        result = validate_json_request(request, QueueRequest)

    response, status_code = result

    assert status_code == HTTPStatus.BAD_REQUEST
    assert response.get_json()["error"] == "Invalid request"
