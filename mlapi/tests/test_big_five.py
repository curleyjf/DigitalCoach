import pytest
from fastapi.testclient import TestClient
from main import app
from tasks.bigfivescore import big_five_feedback, BigFiveScores, TraitLevel
from unittest.mock import patch

client = TestClient(app)


def test_big_five_feedback_function():
    """Test the big_five_feedback function directly"""
    scores = {
        "o": 4.0,  # High openness
        "c": 0.0,  # Medium conscientiousness
        "e": -4.0,  # Low extraversion
        "a": 2.0,  # Medium agreeableness
        "n": 5.0,  # High neuroticism
    }

    # Call the function
    feedback = big_five_feedback(scores)

    # Verify results
    assert len(feedback) == 5  # One feedback item per trait
    assert isinstance(feedback, list)
    assert all(isinstance(item, str) for item in feedback)

    # Check specific feedback based on trait levels
    assert "trying new things" in feedback[0].lower()  # Openness - High
    assert "at your own pace" in feedback[1].lower()  # Conscientiousness - Medium
    assert "struggle to socialize" in feedback[2].lower()  # Extraversion - Low
    assert (
        "but still prioritize yourself" in feedback[3].lower()
    )  # Agreeableness - Medium
    assert "insecure" in feedback[4].lower()  # Neuroticism - High


@patch("routes.big_five.big_five_feedback")
def test_big_five_route_success(mock_big_five_feedback):
    """Test the big_five feedback route with a successful request"""
    # Mock the big_five_feedback function
    mock_big_five_feedback.return_value = [
        "Feedback for openness",
        "Feedback for conscientiousness",
        "Feedback for extraversion",
        "Feedback for agreeableness",
        "Feedback for neuroticism",
    ]

    # Test data
    test_data = {"o": 3.5, "c": 2.7, "e": 4.1, "a": 5.0, "n": 1.2}

    # Make request
    response = client.post("/api/big_five/feedback", json=test_data)

    # Verify response
    assert response.status_code == 200
    data = response.json()
    assert "feedback" in data
    assert len(data["feedback"]) == 5
    assert data["feedback"][0] == "Feedback for openness"

    # Verify the mock was called with correct arguments
    mock_big_five_feedback.assert_called_once()
    call_args = mock_big_five_feedback.call_args[0][0]
    assert call_args["o"] == 3.5
    assert call_args["c"] == 2.7
    assert call_args["e"] == 4.1
    assert call_args["a"] == 5.0
    assert call_args["n"] == 1.2


def test_big_five_route_invalid_input():
    """Test the big_five feedback route with invalid input"""
    # Missing fields
    response = client.post("/api/big_five/feedback", json={"o": 3.5})
    assert response.status_code == 422  # Validation error

    # Invalid types
    response = client.post(
        "/api/big_five/feedback",
        json={"o": "not a number", "c": 2.7, "e": 4.1, "a": 5.0, "n": 1.2},
    )
    assert response.status_code == 422  # Validation error


@patch("routes.big_five.big_five_feedback")
def test_big_five_route_error_handling(mock_big_five_feedback):
    """Test error handling in the big_five feedback route"""
    # Mock the function to raise an exception
    mock_big_five_feedback.side_effect = ValueError("Test error")

    # Test data
    test_data = {"o": 3.5, "c": 2.7, "e": 4.1, "a": 5.0, "n": 1.2}

    # Make request
    response = client.post("/api/big_five/feedback", json=test_data)

    # Verify response
    assert response.status_code == 500
    data = response.json()
    assert "detail" in data
    assert "Failed to generate Big Five feedback" in data["detail"]
