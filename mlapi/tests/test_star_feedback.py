"""
Start the worker in a daemon process. This is required for the tests to work. Then run the route.
Wait for the job to complete then. Get the result using the `api/jobs/results/{job_id}` route
"""

import pytest
import time
from fastapi.testclient import TestClient
from main import app
from tasks.starscores import percentageFeedback

client = TestClient(app)


def test_star_scores():
    """
    Test for the STAR feedback analysis workflow:
    1. Submit text for STAR analysis
    2. Poll until the job is complete
    3. Verify the result has the expected structure
    """
    # Sample text with all STAR components
    test_text = """
    In my previous role, our team faced a critical website outage during a major product launch.
    I was tasked with identifying the cause and implementing a fix within a two-hour window.
    I quickly analyzed server logs, identified a database connection issue, and implemented a 
    connection pooling solution. As a result, we were able to restore service within 90 minutes, 
    allowing the product launch to proceed with minimal disruption.
    """

    # Submit text for analysis
    response = client.post("/api/star_feedback/analyze", json={"text": test_text})
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert "status" in response.json()
    assert response.json()["status"] == "queued"
    job_id = response.json()["job_id"]

    # Poll until job is complete (with timeout)
    start_time = time.time()
    timeout = 30  # 30 second timeout
    result = None

    while time.time() - start_time < timeout:
        response = client.get(f"/api/jobs/results/{job_id}")
        if response.status_code == 200 and response.json().get("status") == "success":
            result = response.json()
            break
        time.sleep(0.5)

    # Assert job completed within timeout
    assert result is not None, "Job did not complete within the timeout period"

    # Verify result structure
    result_data = result.get("result", {})
    assert "fufilledStar" in result_data
    assert "percentages" in result_data
    assert "classifications" in result_data

    # Verify percentages structure
    percentages = result_data["percentages"]
    assert "action" in percentages
    assert "result" in percentages
    assert "situation" in percentages
    assert "task" in percentages

    # Verify classifications structure
    classifications = result_data["classifications"]
    assert isinstance(classifications, list)
    if classifications:
        # Each classification should be a list with two elements: sentence and category
        assert len(classifications[0]) == 2

    # Generate feedback from percentages and verify structure
    feedback = percentageFeedback(percentages)
    assert isinstance(feedback, list)

    # Verify at least one feedback message
    assert len(feedback) > 0

    # Verify all feedback messages are strings
    for msg in feedback:
        assert isinstance(msg, str)
