from http import HTTPStatus

import pydantic
from flask import jsonify
from pydantic import ValidationError


def validate_json_request(
    request,
    EntityRequest: type[pydantic.BaseModel],
):
    """Validate a JSON request and return a parsed payload."""
    if not request.is_json:
        return (
            jsonify({"error": "Content-Type must be application/json"}),
            HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
        )

    try:
        payload = EntityRequest.model_validate(request.get_json())
    except ValidationError as e:
        return (
            jsonify(
                {
                    "error": "Invalid request",
                    "details": e.errors(include_input=False),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    return payload


def validate_query_params(
    request,
    QueryModel: type[pydantic.BaseModel],
):
    """Validate query parameters and return a parsed payload."""
    try:
        return QueryModel.model_validate(request.args.to_dict())
    except ValidationError as e:
        return (
            jsonify(
                {
                    "error": "Invalid query parameters",
                    "details": e.errors(include_input=False),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )
