"""
Tests for the participant removal functionality.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestParticipantRemoval:
    """Test participant removal functionality."""

    def test_remove_existing_participant(self, client, reset_activities):
        """Test successful removal of an existing participant."""
        test_email = "removetest@mergington.edu"
        activity_name = "Chess Club"
        
        # First, sign up the participant
        signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert signup_response.status_code == 200
        
        # Verify participant was added
        response = client.get("/activities")
        data = response.json()
        assert test_email in data[activity_name]["participants"]
        
        # Now remove the participant
        remove_response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert remove_response.status_code == 200
        
        result = remove_response.json()
        assert "message" in result
        assert test_email in result["message"]
        assert activity_name in result["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        assert test_email not in updated_data[activity_name]["participants"]

    def test_remove_from_nonexistent_activity(self, client):
        """Test removal from a non-existent activity."""
        response = client.delete("/activities/NonExistentActivity/remove?email=test@mergington.edu")
        
        assert response.status_code == 404
        result = response.json()
        assert "detail" in result
        assert "Activity not found" in result["detail"]

    def test_remove_nonexistent_participant(self, client):
        """Test removal of a participant who is not signed up."""
        activity_name = "Chess Club"
        test_email = "notregistered@mergington.edu"
        
        response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        
        assert response.status_code == 400
        result = response.json()
        assert "detail" in result
        assert "not signed up" in result["detail"].lower()

    def test_remove_participant_validation_email_parameter(self, client):
        """Test that email parameter is required for removal."""
        response = client.delete("/activities/Chess Club/remove")
        assert response.status_code == 422  # Validation error

    def test_remove_participant_decreases_count(self, client, reset_activities):
        """Test that removing a participant decreases the participant count."""
        test_email = "counttest@mergington.edu"
        activity_name = "Programming Class"
        
        # Get initial participant count
        response = client.get("/activities")
        initial_data = response.json()
        initial_count = len(initial_data[activity_name]["participants"])
        
        # Sign up a participant
        signup_response = client.post(f"/activities/{activity_name}/signup?email={test_email}")
        assert signup_response.status_code == 200
        
        # Verify count increased
        response = client.get("/activities")
        after_signup_data = response.json()
        after_signup_count = len(after_signup_data[activity_name]["participants"])
        assert after_signup_count == initial_count + 1
        
        # Remove the participant
        remove_response = client.delete(f"/activities/{activity_name}/remove?email={test_email}")
        assert remove_response.status_code == 200
        
        # Verify count decreased back to original
        response = client.get("/activities")
        final_data = response.json()
        final_count = len(final_data[activity_name]["participants"])
        assert final_count == initial_count

    def test_remove_existing_default_participant(self, client, reset_activities):
        """Test removal of a participant that exists in the default data."""
        # Use a participant that exists in the default data
        activity_name = "Chess Club"
        existing_email = "michael@mergington.edu"  # This should exist in default data
        
        # Verify participant exists initially
        response = client.get("/activities")
        initial_data = response.json()
        assert existing_email in initial_data[activity_name]["participants"]
        
        # Remove the participant
        remove_response = client.delete(f"/activities/{activity_name}/remove?email={existing_email}")
        assert remove_response.status_code == 200
        
        # Verify participant was removed
        response = client.get("/activities")
        updated_data = response.json()
        assert existing_email not in updated_data[activity_name]["participants"]