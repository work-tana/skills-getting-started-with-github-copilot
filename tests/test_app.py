"""
Test suite for the Mergington High School FastAPI backend.

These tests use pytest and FastAPI's TestClient to verify the core activity
management endpoints. Each test follows the AAA pattern:
- Arrange: set up needed data and state
- Act: call the endpoint under test
- Assert: verify the response and application behavior
"""

import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    original_state = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(copy.deepcopy(original_state))


def test_get_activities_returns_activity_data():
    # Arrange is handled by the fixture
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert isinstance(data["Chess Club"]["participants"], list)
    assert isinstance(data["Programming Class"]["max_participants"], int)


def test_signup_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest_student@test.mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert email in response.json()["message"]

    activity_data = client.get("/activities").json()[activity_name]
    assert email in activity_data["participants"]


def test_duplicate_signup_returns_400():
    # Arrange
    activity_name = "Chess Club"
    email = "pytest_duplicate@test.mergington.edu"

    client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Act
    duplicate_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert duplicate_response.status_code == 400
    assert duplicate_response.json()["detail"] == "Student already signed up"


def test_unregister_removes_participant():
    # Arrange
    activity_name = "Programming Class"
    email = "pytest_remove@test.mergington.edu"

    signup_response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )
    assert signup_response.status_code == 200

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activity_data = client.get("/activities").json()[activity_name]
    assert email not in activity_data["participants"]


def test_unregister_unknown_participant_returns_404():
    # Arrange
    activity_name = "Gym Class"
    email = "pytest_missing@test.mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants/{email}"
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"


def test_signup_to_unknown_activity_returns_404():
    # Arrange
    activity_name = "Nonexistent Activity"
    email = "pytest_unknown@test.mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
