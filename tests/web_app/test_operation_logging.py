from web_app.app import OperationLog, app, db, log_operation
from web_app.app import client_queue


def setup_function():
    with app.app_context():
        db.session.query(OperationLog).delete()
        db.session.commit()
    client_queue.items.clear()


def test_log_operation_persists_all_fields():
    with app.app_context():
        log_operation(
            user_id="user-1",
            structure="queue",
            operation_type="enqueue",
            value=222,
            description="Added 222 to queue",
        )

        log = db.session.query(OperationLog).one()

        assert log.user_id == "user-1"
        assert log.structure == "queue"
        assert log.operation_type == "enqueue"
        assert log.value == "222"
        assert log.description == "Added 222 to queue"
        assert log.timestamp is not None


def test_database_initialization_does_not_delete_operation_logs():
    with app.app_context():
        log_operation(
            user_id="user-1",
            structure="queue",
            operation_type="enqueue",
            value="persistent-value",
            description="Persistent operation",
        )

        db.create_all()

        log = db.session.query(OperationLog).one()
        assert log.value == "persistent-value"


def test_enqueue_endpoint_creates_operation_log():
    client = app.test_client()

    response = client.post(
        "/api/queue",
        json={"user_id": "user-2", "value": "client-222"},
    )

    assert response.status_code == 201

    with app.app_context():
        log = db.session.query(OperationLog).one()

        assert log.user_id == "user-2"
        assert log.structure == "queue"
        assert log.operation_type == "enqueue"
        assert log.value == "client-222"
        assert log.description == "Added client-222 to queue"
