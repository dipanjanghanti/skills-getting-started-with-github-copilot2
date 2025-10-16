"""
Tests for the main API endpoints of the Mergington High School Activities API.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


class TestMainEndpoints:
    """Test the main API endpoints."""

    def test_root_redirect(self, client):
        """Test that root endpoint redirects to static HTML."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_get_activities(self, client):
        """Test retrieving all activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        
        # Check that we have some activities
        assert len(data) > 0
        
        # Check structure of first activity
        first_activity = list(data.values())[0]
        required_fields = ["description", "schedule", "max_participants", "participants"]
        for field in required_fields:
            assert field in first_activity
        
        # Check data types
        assert isinstance(first_activity["description"], str)
        assert isinstance(first_activity["schedule"], str)
        assert isinstance(first_activity["max_participants"], int)
        assert isinstance(first_activity["participants"], list)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that the activities endpoint contains expected default activities."""
        response = client.get("/activities")
        assert response.status_code == 200
        
        data = response.json()
        
        # Check for some expected activities
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]
        for activity in expected_activities:
            assert activity in data