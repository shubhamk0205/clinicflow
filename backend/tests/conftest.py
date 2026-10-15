import os

# Point the app at an isolated SQLite file BEFORE the app (and its engine) is imported,
# so tests never touch the real PostgreSQL database.
os.environ["DATABASE_URL"] = "sqlite:///./test.db"

import pytest
from fastapi.testclient import TestClient

from app.db import Base, engine
from app.main import app


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def appointment_payload():
    return {
        "patient_name": "Aarav Sharma",
        "patient_phone": "9876543210",
        "doctor": "Dr. Mehta",
        "department": "CARDIOLOGY",
        "scheduled_at": "2026-11-02T10:30:00+05:30",
        "reason": "Routine heart check-up",
    }
