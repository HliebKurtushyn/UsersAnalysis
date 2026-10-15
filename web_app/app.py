from datetime import datetime, timezone
from http import HTTPStatus

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

from .schemas import PushTransactionRequest, QueueRequest, QueueQuery, TransactionsQuery
from .structures import Queue, Stack
from .utils import validate_json_request, validate_query_params


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

client_queue = Queue()
transaction_stack = Stack()


class OperationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    structure = db.Column(db.String(20), nullable=False)
    operation_type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.String(255))


@app.get("/")
def index():
    return render_template(
        "index.html", queue=client_queue.items, stack=transaction_stack.items
    ), HTTPStatus.OK


@app.post("/api/queue")
def enqueue_client():
    payload = validate_json_request(request, QueueRequest)
    if isinstance(payload, tuple):
        return payload

    client_queue.enqueue(payload.value)

    return jsonify({"value": payload.value}), HTTPStatus.CREATED


@app.delete("/api/queue/dequeue")
def dequeue_client():
    payload = validate_json_request(request, QueueRequest)
    if isinstance(payload, tuple):
        return payload

    client_queue.dequeue()

    return jsonify({"value": payload.value}), HTTPStatus.OK


@app.post("/api/transactions")
def push_transaction():
    payload = validate_json_request(request, PushTransactionRequest)
    if isinstance(payload, tuple):
        return payload

    transaction_stack.push(payload.value)

    return jsonify({"value": payload.value}), HTTPStatus.CREATED


@app.get("/api/transactions/pop")
def pop_transaction():
    payload = validate_json_request(request, PushTransactionRequest)
    if isinstance(payload, tuple):
        return payload

    transaction_stack.pop()

    return jsonify({"value": payload.value}), HTTPStatus.OK


@app.get("/api/queue")
def get_queue():
    params = validate_query_params(request, QueueQuery)

    if isinstance(params, tuple):
        return params

    items = client_queue.items
    if params.limit is not None:
        items = items[: params.limit]

    return jsonify({"items": items}), HTTPStatus.OK


@app.get("/api/transactions")
def get_transactions():
    params = validate_query_params(request, TransactionsQuery)

    if isinstance(params, tuple):
        return params

    items = transaction_stack.items
    if params.limit is not None:
        items = items[: params.limit]

    return jsonify({"items": items}), HTTPStatus.OK


with app.app_context():
    db.create_all()
