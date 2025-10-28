import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    """Test that root endpoint redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert all(isinstance(activity["participants"], list) for activity in data.values())

def test_signup_for_activity():
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Signed up test@mergington.edu for Chess Club"

    # Verify participant was added
    activities = client.get("/activities").json()
    assert "test@mergington.edu" in activities["Chess Club"]["participants"]

def test_signup_duplicate():
    """Test signing up for an activity twice"""
    # First signup
    client.post(
        "/activities/Programming Class/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    
    # Try to signup again
    response = client.post(
        "/activities/Programming Class/signup",
        params={"email": "duplicate@mergington.edu"}
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]

def test_signup_nonexistent_activity():
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/NonexistentClub/signup",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]

def test_unregister_from_activity():
    """Test unregistering from an activity"""
    # First sign up
    email = "unregister@mergington.edu"
    activity = "Art Club"
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # Then unregister
    response = client.post(
        f"/activities/{activity}/unregister",
        params={"email": email}
    )
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity}"

    # Verify participant was removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]

def test_unregister_not_registered():
    """Test unregistering when not registered"""
    response = client.post(
        "/activities/Chess Club/unregister",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]

def test_unregister_nonexistent_activity():
    """Test unregistering from a non-existent activity"""
    response = client.post(
        "/activities/NonexistentClub/unregister",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]