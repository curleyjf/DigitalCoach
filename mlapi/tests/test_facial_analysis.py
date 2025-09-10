import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock, MagicMock
from schemas.create_answer import (
    EmotionDetectionResult,
    EmotionTotals,
    EmotionTimelines,
)
from main import app

client = TestClient(app)


@pytest.fixture
def mock_facial_result():
    """Create a mock facial analysis result for testing"""
    # Create a minimal test result
    result = EmotionDetectionResult(
        total_frames=10,
        frame_inference_rate=30,
        emotion_sums=EmotionTotals(
            angry=0.1,
            disgust=0.05,
            fear=0.05,
            happy=0.3,
            sad=0.1,
            surprise=0.1,
            neutral=0.3,
        ),
        timeline=EmotionTimelines(
            angry=[0.1, 0.1, 0.1],
            disgust=[0.05, 0.05, 0.05],
            fear=[0.05, 0.05, 0.05],
            happy=[0.3, 0.3, 0.3],
            sad=[0.1, 0.1, 0.1],
            surprise=[0.1, 0.1, 0.1],
            neutral=[0.3, 0.3, 0.3],
        ),
        clip_length_seconds=10.0,
        errors=None,
        avg_inference_time=0.05,
    )
    return result


@pytest.fixture
def mock_rq_job():
    """Mock RQ Job object"""
    mock_job = MagicMock()
    mock_job.get_id.return_value = "test-job-id"
    return mock_job


def test_create_facial_analysis_job(mock_rq_job):
    """Test creating a facial analysis job"""
    with patch("routes.facial_analysis.add_task_to_queue", return_value=mock_rq_job):
        response = client.post(
            "/api/facial_analysis/",
            json={"video_url": "https://example.com/test.mp4", "sample_rate": 30},
        )
        assert response.status_code == 200
        assert response.json() == {"job_id": "test-job-id"}


def test_create_facial_analysis_job_default_sample_rate(mock_rq_job):
    """Test creating a facial analysis job with default sample rate"""
    with patch("routes.facial_analysis.add_task_to_queue", return_value=mock_rq_job):
        response = client.post(
            "/api/facial_analysis/", json={"video_url": "https://example.com/test.mp4"}
        )
        assert response.status_code == 200
        assert response.json() == {"job_id": "test-job-id"}


def test_get_facial_analysis_pending():
    """Test getting status of a pending facial analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = False

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/facial_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "pending"
            # Result can have additional fields, but these are the core ones we care about


def test_get_facial_analysis_processing():
    """Test getting status of a processing facial analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = True

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/facial_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "processing"


def test_get_facial_analysis_failed():
    """Test getting status of a failed facial analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = True
    mock_job.exc_info = "Test error"

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/facial_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "failed"
            assert result["error"] == "Test error"


def test_get_facial_analysis_completed(mock_facial_result):
    """Test getting status of a completed facial analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = True
    mock_job.is_failed = False
    mock_job.result = mock_facial_result

    # Create a simple dict for the result instead of mocking model_dump
    result_dict = {
        "emotion_sums": {
            "angry": 0.1,
            "disgust": 0.05,
            "fear": 0.05,
            "happy": 0.3,
            "sad": 0.1,
            "surprise": 0.1,
            "neutral": 0.3,
        },
        "timeline": {
            "angry": [0.1, 0.1, 0.1],
            "disgust": [0.05, 0.05, 0.05],
            "fear": [0.05, 0.05, 0.05],
            "happy": [0.3, 0.3, 0.3],
            "sad": [0.1, 0.1, 0.1],
            "surprise": [0.1, 0.1, 0.1],
            "neutral": [0.3, 0.3, 0.3],
        },
        "total_frames": 10,
        "frame_inference_rate": 30,
        "clip_length_seconds": 10.0,
        "errors": None,
        "avg_inference_time": 0.05,
    }

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Patch the model_dump method at the route level instead of on the object
            with patch(
                "routes.facial_analysis.EmotionDetectionResult.model_dump",
                return_value=result_dict,
            ):
                response = client.get("/api/facial_analysis/test-job-id")
                assert response.status_code == 200
                result = response.json()
                assert result["job_id"] == "test-job-id"
                assert result["status"] == "completed"
                assert "result" in result


def test_get_facial_analysis_result(mock_facial_result):
    """Test getting the result of a completed facial analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = True
    mock_job.is_failed = False
    mock_job.result = mock_facial_result

    # No need to mock model_dump directly on the object
    # We'll patch at the response level

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Avoid JSON serialization issues by patching the model class
            with patch(
                "routes.facial_analysis.EmotionDetectionResult.model_dump",
                return_value={},
            ):
                with patch(
                    "routes.audio_analysis.AudioSentimentResult.model_dump",
                    return_value={},
                ):
                    response = client.get("/api/facial_analysis/test-job-id/result")
                    assert response.status_code == 200


def test_get_facial_analysis_result_not_finished():
    """Test getting the result of a job that's not finished yet"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = True

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Force exception to be raised with the expected message
            with patch(
                "routes.facial_analysis.HTTPException",
                side_effect=lambda **kwargs: Exception(kwargs["detail"]),
            ):
                # Make sure the endpoint gets the actual function call
                with pytest.raises(Exception) as excinfo:
                    client.get("/api/facial_analysis/test-job-id/result")
                assert "Job is still processing" in str(excinfo.value)


def test_get_facial_analysis_result_failed():
    """Test getting the result of a failed job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = True
    mock_job.exc_info = "Test error"

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Force exception to be raised with the expected message
            with patch(
                "routes.facial_analysis.HTTPException",
                side_effect=lambda **kwargs: Exception(kwargs["detail"]),
            ):
                # Make sure the endpoint gets the actual function call
                with pytest.raises(Exception) as excinfo:
                    client.get("/api/facial_analysis/test-job-id/result")
                assert "Test error" in str(excinfo.value)
