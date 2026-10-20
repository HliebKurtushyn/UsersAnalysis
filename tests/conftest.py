import os
from pathlib import Path


TEST_DATABASE_PATH = (
    Path(os.environ.get("TMPDIR", "/tmp")) / f"users_analysis_test_{os.getpid()}.db"
)
TEST_DATABASE_PATH.unlink(missing_ok=True)
os.environ["BANKING_DATABASE_PATH"] = str(TEST_DATABASE_PATH)


def pytest_sessionfinish(session, exitstatus):
    TEST_DATABASE_PATH.unlink(missing_ok=True)
