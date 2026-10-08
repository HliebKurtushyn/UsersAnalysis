from datetime import datetime, timezone

from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy

from .structures import Queue, Stack

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
    return render_template("index.html")


@app.post("/api/queue")
def enqueue_client():
    value = request.json.get("value")
    client_queue.enqueue(value)
    return jsonify({"value": value}), 201


@app.post("/api/transactions")
def push_transaction():
    value = request.json.get("value")
    transaction_stack.push(value)
    return jsonify({"value": value}), 201


with app.app_context():
    db.create_all()
