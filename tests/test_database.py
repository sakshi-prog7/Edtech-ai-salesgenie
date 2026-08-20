import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from main import app
from db.database import engine, Base
from scripts.seed_database import seed_all_datasets

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Ensures database tables are created and seeded before running test suite on CI."""
    seed_all_datasets()
    yield

def test_database_tables_populated():
    tables = [
        "student_performance",
        "student_dropout",
        "online_learning_engagement",
        "marketing_campaign_performance"
    ]
    with engine.connect() as conn:
        for tbl in tables:
            count = conn.execute(text(f"SELECT COUNT(*) FROM {tbl}")).scalar()
            assert count > 0, f"Table {tbl} is empty"

def test_auth_and_login_flow():
    reg_res = client.post("/api/auth/register", json={
        "full_name": "Counselor Varun",
        "email": "varun.crm@edtech.com",
        "password": "Password123",
        "role": "admissions_admin"
    })
    assert reg_res.status_code in [200, 400]

    login_res = client.post("/api/auth/login", json={
        "email": "varun.crm@edtech.com",
        "password": "Password123"
    })
    assert login_res.status_code == 200
    assert login_res.json()["status"] == "success"

def test_dashboard_calculations():
    res = client.get("/api/dashboard/overview")
    assert res.status_code == 200
    data = res.json()
    assert data["total_leads"] > 0
    assert data["overall_roi_percentage"] > 0