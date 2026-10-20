"""Temporarily add demo operation logs to the production database.

Usage:
    .venv/bin/python -m scripts.seed_test_logs --count 100
"""

import argparse

from web_app.app import app, db
from web_app.models import OperationLog


USERS = ("user-1", "user-2", "user-3")
OPERATIONS = (
    ("queue", "enqueue"),
    ("queue", "dequeue"),
    ("stack", "push"),
    ("stack", "pop"),
)


def create_demo_logs(count: int) -> None:
    """Create demo logs without deleting existing records."""
    logs = []
    for index in range(count):
        structure, operation_type = OPERATIONS[index % len(OPERATIONS)]
        user_id = USERS[index % len(USERS)]
        value = f"demo-{index + 1:04d}"
        logs.append(
            OperationLog(
                user_id=user_id,
                structure=structure,
                operation_type=operation_type,
                value=value,
                description=f"Demo {operation_type} for {value}",
                is_undone=False,
            )
        )

    db.session.add_all(logs)
    db.session.commit()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--count",
        type=int,
        default=100,
        help="number of demo logs to add (default: 100)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.count < 1:
        raise SystemExit("--count must be a positive integer")

    if app.config.get("TESTING"):
        raise SystemExit(
            "Refusing to seed logs while USERS_ANALYSIS_TESTING=1 is enabled"
        )

    with app.app_context():
        create_demo_logs(args.count)
        total = db.session.query(OperationLog).count()

    print(f"Added {args.count} demo logs. Total logs: {total}")


if __name__ == "__main__":
    main()
