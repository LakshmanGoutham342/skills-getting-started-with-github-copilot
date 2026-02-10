import os
import sys

# Ensure src is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from fastapi.testclient import TestClient
from app import app


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    # Basic expected activity exists
    assert "Basketball" in data


def test_signup_and_unregister_flow():
    activity = "Basketball"
    email = "test.student@example.com"

    # Ensure email not already present (if it is, try to remove first)
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    if email in participants:
        client.delete(f"/activities/{activity}/unregister?email={email}")

    # Sign up
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 200
    assert resp.json()["message"]

    # Confirm present
    resp = client.get("/activities")
    assert resp.status_code == 200
    participants = resp.json()[activity]["participants"]
    assert email in participants

    # Duplicate signup should fail
    resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert resp.status_code == 400

    # Unregister
    resp = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert resp.status_code == 200

    # Confirm removed
    resp = client.get("/activities")
    participants = resp.json()[activity]["participants"]
    assert email not in participants
