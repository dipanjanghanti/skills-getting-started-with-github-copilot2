"""
Test configuration and fixtures for the Mergington High School Activities API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activities():
    """Sample activities data for testing."""
    return {
        "Test Activity 1": {
            "description": "A test activity for unit testing",
            "schedule": "Test schedule",
            "max_participants": 5,
            "participants": ["test1@mergington.edu", "test2@mergington.edu"]
        },
        "Test Activity 2": {
            "description": "Another test activity",
            "schedule": "Another test schedule",
            "max_participants": 3,
            "participants": []
        }
    }


@pytest.fixture
def reset_activities():
    """Reset activities to original state after each test."""
    from src.app import activities
    original_activities = activities.copy()
    yield
    activities.clear()
    activities.update(original_activities)