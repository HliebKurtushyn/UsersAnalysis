from datetime import datetime, timezone
from http import HTTPStatus
from pathlib import Path

from flask import Flask, jsonify, render_template, request
import joblib
from flask_sqlalchemy import SQLAlchemy
from ml_pipeline.recommender import top_products
from ml_pipeline.prepare_data import prepare_data
from ml_pipeline.train import CLEANED_DATA_PATH, RAW_DATA_PATH, train
from pydantic import ValidationError

from .config import Config
from .schemas import (
    PushTransactionRequest,
    PrepareDataRequest,
    QueueQuery,
    QueueRequest,
    LogsQuery,
    StructureOperationRequest,
    TransactionsQuery,
)
from .structures import Queue, Stack
from .utils import validate_json_request, validate_query_params


app = Flask(__name__)
app.config.from_object(Config)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///banking.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

client_queue = Queue()
transaction_stack = Stack()
ARTIFACTS_DIR = Path(__file__).resolve().parent.parent / "artifacts"
ML_ARTIFACT_NAMES = (
    "engagement_model",
    "user_features",
    "product_features",
    "user_clusters",
    "product_clusters",
    "metadata",
)


class OperationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False)
    structure = db.Column(db.String(20), nullable=False)
    operation_type = db.Column(db.String(20), nullable=False)
    value = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    description = db.Column(db.String(255))
    is_undone = db.Column(db.Boolean, default=False)


def log_operation(user_id, structure, operation_type, value, description):
    """Log an operation performed on a structure."""
    log = OperationLog(
        user_id=user_id,
        structure=structure,
        operation_type=operation_type,
        value=str(value),
        description=description,
    )

    db.session.add(log)
    db.session.commit()


@app.context_processor
def inject_global_variables():
    return {"product_version": app.config["PRODUCT_VERSION"]}


def _load_artifact(name):
    path = ARTIFACTS_DIR / f"{name}.joblib"
    return joblib.load(path) if path.exists() else None


def _with_rates(records):
    for record in records:
        views = record.get("views", 0) or 0
        purchases = record.get("purchases", 0) or 0
        record["conversion_rate"] = purchases / views if views > 0 else 0
    return records


@app.get("/")
def index():
    return render_template(
        "dashboard.html", queue=client_queue.items, stack=transaction_stack.items
    ), HTTPStatus.OK


@app.get("/queue")
def queue_page():
    return render_template("queue.html", queue=client_queue.items), HTTPStatus.OK


@app.get("/transactions")
def transactions_page():
    return render_template(
        "transactions.html",
        stack=transaction_stack.items,
    ), HTTPStatus.OK


@app.get("/logs")
def logs_page():
    return render_template("logs.html"), HTTPStatus.OK


@app.get("/logs/export/json")
def export_logs_json():
    logs = OperationLog.query.order_by(OperationLog.timestamp.desc()).all()
    data = {}

    for log in logs:
        data[log.id] = {
            "user_id": log.user_id,
            "structure": log.structure,
            "operation_type": log.operation_type,
            "value": log.value,
            "timestamp": log.timestamp.isoformat() if log.timestamp else None,
            "description": log.description,
            "is_undone": log.is_undone,
        }

    response = jsonify(data)
    response.headers["Content-Disposition"] = 'attachment; filename="logs.json"'

    return response


@app.get("/analytics")
def analytics_page():
    operation_counts = {
        operation: OperationLog.query.filter_by(operation_type=operation).count()
        for operation in ("enqueue", "dequeue", "push", "pop")
    }
    structure_counts = {
        structure: OperationLog.query.filter_by(structure=structure).count()
        for structure in ("queue", "stack")
    }
    return render_template(
        "analytics.html",
        operation_counts=operation_counts,
        structure_counts=structure_counts,
        total_operations=OperationLog.query.count(),
    ), HTTPStatus.OK


@app.get("/products")
def products_page():
    product_features = _load_artifact("product_features")
    product_clusters = _load_artifact("product_clusters")

    sort_by = request.args.get("sort_by", "product_id")
    order = request.args.get("order", "asc")
    cluster_filter = request.args.get("cluster", "")
    allowed_sort_columns = {
        "product_id",
        "views",
        "carts",
        "purchases",
        "conversion_rate",
    }
    if sort_by not in allowed_sort_columns:
        sort_by = "product_id"
    if order not in {"asc", "desc"}:
        order = "asc"

    products = []
    if product_features is not None:
        products = _with_rates(product_features.to_dict("records"))
        if cluster_filter and product_clusters is not None:
            cluster_records = product_clusters.to_dict("records")
            cluster_ids = {
                row["product_id"]
                for row in cluster_records
                if str(row["cluster"]) == cluster_filter
            }
            products = [row for row in products if row["product_id"] in cluster_ids]
        products.sort(key=lambda row: row.get(sort_by, 0), reverse=order == "desc")

    cluster_ids = (
        sorted(product_clusters["cluster"].unique().tolist())
        if product_clusters is not None
        else []
    )

    return render_template(
        "products.html",
        product_features=products,
        product_clusters=(
            product_clusters.to_dict("records") if product_clusters is not None else []
        ),
        artifacts_available=product_features is not None,
        sort_by=sort_by,
        order=order,
        cluster_filter=cluster_filter,
        cluster_ids=cluster_ids,
    ), HTTPStatus.OK


@app.get("/users")
def users_page():
    user_features = _load_artifact("user_features")
    user_clusters = _load_artifact("user_clusters")
    users = []
    cluster_filter = request.args.get("cluster", "")
    engagement_filter = request.args.get("engagement", "")
    sort_by = request.args.get("sort_by", "user_id")
    order = request.args.get("order", "asc")

    if user_features is not None:
        if user_clusters is not None:
            users = user_features.merge(
                user_clusters,
                on="user_id",
                how="left",
            ).to_dict("records")
        else:
            users = user_features.to_dict("records")
        for user in users:
            user["engagement"] = "High" if user.get("purchases", 0) >= 1 else "Low"
        if cluster_filter:
            users = [u for u in users if str(u.get("cluster")) == cluster_filter]
        if engagement_filter in {"High", "Low"}:
            users = [u for u in users if u["engagement"] == engagement_filter]
        allowed_sort_columns = {"user_id", "views", "carts", "purchases"}
        if sort_by not in allowed_sort_columns:
            sort_by = "user_id"
        if order not in {"asc", "desc"}:
            order = "asc"
        users.sort(key=lambda row: row.get(sort_by, 0), reverse=order == "desc")

    cluster_ids = (
        sorted(user_clusters["cluster"].unique().tolist())
        if user_clusters is not None
        else []
    )

    return render_template(
        "users.html",
        users=users,
        artifacts_available=user_features is not None,
        cluster_filter=cluster_filter,
        engagement_filter=engagement_filter,
        sort_by=sort_by,
        order=order,
        cluster_ids=cluster_ids,
    ), HTTPStatus.OK


@app.get("/ml")
def ml_overview_page():
    statuses = {name: (_load_artifact(name) is not None) for name in ML_ARTIFACT_NAMES}
    user_features = _load_artifact("user_features")
    product_features = _load_artifact("product_features")
    metadata = _load_artifact("metadata") or {}
    return render_template(
        "ml_overview.html",
        statuses=statuses,
        user_count=len(user_features) if user_features is not None else 0,
        product_count=len(product_features) if product_features is not None else 0,
        metadata=metadata,
        metrics=metadata.get("model_metrics", {}),
        class_counts=metadata.get("class_counts", {}),
    ), HTTPStatus.OK


@app.post("/api/ml/train")
def train_ml_pipeline():
    train()
    return jsonify(
        {"message": "ML artifacts were recreated successfully."}
    ), HTTPStatus.OK


@app.post("/api/ml/prepare-data")
def prepare_ml_dataset():
    payload = validate_json_request(request, PrepareDataRequest)
    if isinstance(payload, tuple):
        return payload

    try:
        output_path = prepare_data(
            source_path=RAW_DATA_PATH,
            output_path=CLEANED_DATA_PATH,
            rows=payload.rows,
        )
    except FileNotFoundError as error:
        return jsonify({"error": str(error)}), HTTPStatus.NOT_FOUND
    except ValueError as error:
        return jsonify({"error": str(error)}), HTTPStatus.BAD_REQUEST

    return jsonify(
        {
            "message": "Cleaned dataset was recreated successfully.",
            "path": str(output_path),
            "rows": payload.rows,
        }
    ), HTTPStatus.OK


@app.get("/recommendations")
def recommendations_page():
    product_features = _load_artifact("product_features")
    recommendations = []
    if product_features is not None:
        recommendations = _with_rates(
            top_products(product_features, limit=10).to_dict("records")
        )
    return render_template(
        "recommendations.html",
        recommendations=recommendations,
        artifacts_available=product_features is not None,
    ), HTTPStatus.OK


@app.post("/api/queue")
def enqueue_client():
    payload = validate_json_request(request, QueueRequest)
    if isinstance(payload, tuple):
        return payload

    client_queue.enqueue(payload.value)

    log_operation(
        user_id=payload.user_id,
        structure="queue",
        operation_type="enqueue",
        value=payload.value,
        description=f"Added {payload.value} to queue",
    )

    return jsonify({"value": payload.value}), HTTPStatus.CREATED


@app.delete("/api/queue/dequeue")
def dequeue_client():
    payload = validate_json_request(request, StructureOperationRequest)
    if isinstance(payload, tuple):
        return payload

    value = client_queue.dequeue()
    if value is None:
        return jsonify({"error": "Queue is empty"}), HTTPStatus.NOT_FOUND

    log_operation(
        user_id=payload.user_id,
        structure="queue",
        operation_type="dequeue",
        value=value,
        description=f"Removed {value} from queue",
    )

    return jsonify({"value": value}), HTTPStatus.OK


@app.post("/api/transactions")
def push_transaction():
    payload = validate_json_request(request, PushTransactionRequest)
    if isinstance(payload, tuple):
        return payload

    transaction_stack.push(payload.value)

    log_operation(
        user_id=payload.user_id,
        structure="stack",
        operation_type="push",
        value=payload.value,
        description=f"Added {payload.value} to queue",
    )

    return jsonify({"value": payload.value}), HTTPStatus.CREATED


@app.delete("/api/transactions/pop")
def pop_transaction():
    payload = validate_json_request(request, StructureOperationRequest)
    if isinstance(payload, tuple):
        return payload

    value = transaction_stack.pop()
    if value is None:
        return jsonify({"error": "Stack is empty"}), HTTPStatus.NOT_FOUND

    log_operation(
        user_id=payload.user_id,
        structure="stack",
        operation_type="pop",
        value=value,
        description=f"Removed {value} from stack",
    )

    return jsonify({"value": value}), HTTPStatus.OK


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


@app.get("/api/logs")
def get_operation_logs():
    query_params = {
        key: value for key, value in request.args.to_dict().items() if value.strip()
    }
    try:
        params = LogsQuery.model_validate(query_params)
    except ValidationError as error:
        return (
            jsonify(
                {
                    "error": "Invalid query parameters",
                    "details": error.errors(include_input=False),
                }
            ),
            HTTPStatus.BAD_REQUEST,
        )

    query = OperationLog.query
    if params.user_id is not None:
        query = query.filter_by(user_id=params.user_id)
    if params.operation_type is not None:
        query = query.filter_by(operation_type=params.operation_type)

    logs = query.order_by(OperationLog.timestamp.desc()).all()
    return jsonify(
        {
            "items": [
                {
                    "id": log.id,
                    "user_id": log.user_id,
                    "structure": log.structure,
                    "operation_type": log.operation_type,
                    "value": log.value,
                    "timestamp": (log.timestamp.isoformat() if log.timestamp else None),
                    "description": log.description,
                    "is_undone": log.is_undone,
                }
                for log in logs
            ]
        }
    ), HTTPStatus.OK


@app.post("/api/undo")
def undo_last_operation():
    """Undo the last operation (enqueue, dequeue, push, or pop)."""
    payload = validate_json_request(request, StructureOperationRequest)
    if isinstance(payload, tuple):
        return payload

    last_log = (
        OperationLog.query.filter(
            OperationLog.user_id == payload.user_id,
            OperationLog.is_undone.is_(False),
            OperationLog.operation_type != "undo",
        )
        .order_by(OperationLog.timestamp.desc())
        .first()
    )

    if not last_log:
        return jsonify({"error": "No operation to undo"}), HTTPStatus.NOT_FOUND

    try:
        if last_log.operation_type == "enqueue":
            value = client_queue.dequeue()
            if value != last_log.value:
                client_queue.items.insert(0, value)
                if last_log.value in client_queue.items:
                    client_queue.items.remove(last_log.value)
                else:
                    return jsonify(
                        {"error": "Cannot undo: value not found in queue"}
                    ), HTTPStatus.CONFLICT

        elif last_log.operation_type == "dequeue":
            client_queue.items.insert(0, last_log.value)

        elif last_log.operation_type == "push":
            value = transaction_stack.pop()
            if value != last_log.value:
                transaction_stack.items.append(value)
                if last_log.value in transaction_stack.items:
                    transaction_stack.items.remove(last_log.value)
                else:
                    return jsonify(
                        {"error": "Cannot undo: value not found in stack"}
                    ), HTTPStatus.CONFLICT

        elif last_log.operation_type == "pop":
            transaction_stack.push(last_log.value)

        else:
            return jsonify(
                {"error": f"Cannot undo operation type: {last_log.operation_type}"}
            ), HTTPStatus.BAD_REQUEST

        last_log.is_undone = True
        db.session.commit()

        log_operation(
            user_id=payload.user_id,
            structure=last_log.structure,
            operation_type="undo",
            value=last_log.value,
            description=f"Undid {last_log.operation_type} of {last_log.value}",
        )

        return jsonify(
            {
                "message": "Operation undone successfully",
                "undone_operation": {
                    "id": last_log.id,
                    "operation_type": last_log.operation_type,
                    "structure": last_log.structure,
                    "value": last_log.value,
                },
            }
        ), HTTPStatus.OK

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), HTTPStatus.INTERNAL_SERVER_ERROR


with app.app_context():
    db.create_all()
