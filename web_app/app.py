from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

from .schemas import PushTransactionRequest, QueueRequest
from .structures import Queue, Stack

from pydantic import ValidationError

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
    return render_template("index.html", queue=client_queue.items, stack=transaction_stack.items)


@app.post("/api/queue")
def enqueue_client():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        payload = QueueRequest.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({
            "error": "Invalid request",
            "details": e.errors(include_input=False)
        }), 400

    client_queue.enqueue(payload.value)
    return jsonify({"value": payload.value}), 201


@app.post("/api/transactions")
def push_transaction():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    try:
        payload = PushTransactionRequest.model_validate(request.get_json())
    except ValidationError as e:
        return jsonify({
            "error": "Invalid request",
            "details": e.errors(include_input=False)
        }), 400

    transaction_stack.push(payload.value)
    return jsonify({"value": payload.value}), 201


with app.app_context():
    db.create_all()
