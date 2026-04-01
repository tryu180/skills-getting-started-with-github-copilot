from fastapi.testclient import TestClient
import pytest

from src.app import app, activities

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"],
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"],
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"],
    },
}


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update({
        k: {
            "description": v["description"],
            "schedule": v["schedule"],
            "max_participants": v["max_participants"],
            "participants": list(v["participants"]),
        }
        for k, v in INITIAL_ACTIVITIES.items()
    })


client = TestClient(app)


def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert "Programming Class" in body
    assert "Gym Class" in body


def test_signup_for_activity_success():
    new_email = "newstudent@mergington.edu"
    response = client.post("/activities/Chess Club/signup", params={"email": new_email})
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for Chess Club"
    assert new_email in activities["Chess Club"]["participants"]


def test_signup_duplicate():
    email = "daniel@mergington.edu"
    response1 = client.post("/activities/Chess Club/signup", params={"email": email})
    assert response1.status_code == 400
    assert "already signed up" in response1.json()["detail"]


def test_remove_participant_success():
    existing = "michael@mergington.edu"
    response = client.delete("/activities/Chess Club/participants", params={"email": existing})
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {existing} from Chess Club"
    assert existing not in activities["Chess Club"]["participants"]


def test_remove_participant_not_found():
    response = client.delete("/activities/Chess Club/participants", params={"email": "ghost@mergington.edu"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
