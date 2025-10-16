"""
Tests for the activity signup functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestActivitySignup:
    """Test activity signup functionality."""

    def test_signup_for_existing_activity(self, client, reset_activities):
        """Test successful signup for an existing activity."""
        # Get an activity with available spots
        response = client.get("/activities")
        data = response.json()
        
        # Find an activity with available spots
        activity_name = None
        for name, details in data.items():
            if len(details["participants"]) < details["max_participants"]:
                activity_name = name
                break
        
        assert activity_name is not None, "No activities with available spots found"
        
        # Test signup
        test_email = "newstudent@mergington.edu"
        response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        
        assert response.status_code == 200
        result = response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert activity_name in result["message"]

    def test_signup_for_nonexistent_activity(self, client):
        """Test signup for a non-existent activity."""
        response = client.post("/activities/NonExistentActivity/signup?email=test@mergington.edu")
        
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_signup_duplicate_prevents_multiple_registrations(self, client, reset_activities):
        """Test that a student cannot sign up for multiple activities."""
        # Get two different activities
        response = client.get("/activities")
        data = response.json()
        
        activity_names = list(data.keys())[:2]
        assert len(activity_names) >= 2, "Need at least 2 activities for this test"
        
        test_email = "duplicatetest@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(f"/activities/{activity_names[0]}/signup?email={test_email}")
        assert response1.status_code == 200
        
        # Try to sign up for second activity (should fail)
        response2 = client.post(f"/activities/{activity_names[1]}/signup?email={test_email}")
        assert response2.status_code == 400
        result = response2.json()
        assert "already signed up" in result["detail"].lower()

    def test_signup_validation_email_parameter(self, client):
        """Test that email parameter is required."""
        response = client.post("/activities/Chess Club/signup")
        assert response.status_code == 422  # Validation error

    def test_signup_participant_appears_in_activity_list(self, client, reset_activities):
        """Test that after signup, participant appears in the activity list."""
        test_email = "listtest@mergington.edu"
        activity_name = "Chess Club"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_participants = initial_data[activity_name]["participants"].copy()
        
        # Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert signup_response.status_code == 200
        
        # Check that participant was added
        response = client.get("/activities")
        updated_data = response.json()
        updated_participants = updated_data[activity_name]["participants"]
        
        assert test_email in updated_participants
        assert len(updated_participants) == len(initial_participants) + 1