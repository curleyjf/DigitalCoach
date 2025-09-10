import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from schemas.create_answer import AudioSentimentResult
from main import app

client = TestClient(app)


@pytest.fixture
def mock_audio_result():
    """Create a mock audio analysis result for testing"""
    from schemas.create_answer import (
        SentimentResult,
        HighlightData,
        TimestampData,
        IABLabel,
        IABResult,
    )

    # Create a minimal test result
    result = AudioSentimentResult(
        sentiment_analysis=[
            SentimentResult(
                text="This is a test",
                sentiment="NEUTRAL",
                confidence=0.95,
                start=1000,
                end=2000,
            ),
            SentimentResult(
                text="Another test segment",
                sentiment="POSITIVE",
                confidence=0.85,
                start=2100,
                end=3000,
            ),
        ],
        highlights=[
            HighlightData(
                text="test",
                rank=0.8,
                count=2,
                timestamps=[
                    TimestampData(start=1200, end=1300),
                    TimestampData(start=2200, end=2300),
                ],
            )
        ],
        iab_results=IABResult(
            text="This is a test transcript",
            labels=[IABLabel(label="Technology", relevance=0.9)],
        ),
        clip_length_seconds=10.0,
        errors=None,
    )
    return result


@pytest.fixture
def mock_rq_job():
    """Mock RQ Job object"""
    mock_job = MagicMock()
    mock_job.get_id.return_value = "test-job-id"
    return mock_job


def test_create_audio_analysis_job(mock_rq_job):
    """Test creating an audio analysis job"""
    with patch("routes.audio_analysis.add_task_to_queue", return_value=mock_rq_job):
        response = client.post(
            "/api/audio_analysis/", json={"video_url": "https://example.com/test.mp4"}
        )
        assert response.status_code == 200
        assert response.json() == {"job_id": "test-job-id"}


def test_get_audio_analysis_pending():
    """Test getting status of a pending audio analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = False

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/audio_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "pending"
            # Result can have additional fields, but these are the core ones we care about


def test_get_audio_analysis_processing():
    """Test getting status of a processing audio analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = True

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/audio_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "processing"


def test_get_audio_analysis_failed():
    """Test getting status of a failed audio analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = True
    mock_job.exc_info = "Test error"

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            response = client.get("/api/audio_analysis/test-job-id")
            assert response.status_code == 200
            result = response.json()
            assert result["job_id"] == "test-job-id"
            assert result["status"] == "failed"
            assert result["error"] == "Test error"


def test_get_audio_analysis_completed(mock_audio_result):
    """Test getting status of a completed audio analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = True
    mock_job.is_failed = False
    mock_job.result = mock_audio_result

    # Create a simple dict for the result instead of mocking model_dump
    result_dict = {
        "sentiment_analysis": [{"text": "Test"}],
        "highlights": [],
        "iab_results": {"text": "", "labels": []},
        "clip_length_seconds": 10.0,
        "errors": None,
    }

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Patch the dict/model_dump method at the route level instead of on the object
            with patch(
                "routes.audio_analysis.AudioSentimentResult.model_dump",
                return_value=result_dict,
            ):
                response = client.get("/api/audio_analysis/test-job-id")
                assert response.status_code == 200
                result = response.json()
                assert result["job_id"] == "test-job-id"
                assert result["status"] == "completed"
                assert "result" in result


def test_get_audio_analysis_result(mock_audio_result):
    """Test getting the result of a completed audio analysis job"""
    mock_job = MagicMock()
    mock_job.is_finished = True
    mock_job.is_failed = False
    mock_job.result = mock_audio_result

    # Create a mock for the model itself to isolate test from implementation
    result_dict = {
        "sentiment_analysis": [{"text": "Test"}],
        "highlights": [],
        "iab_results": {"text": "", "labels": []},
        "clip_length_seconds": 10.0,
        "errors": None,
    }

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Replace the actual return value with a simple dict to avoid serialization issues
            with patch.object(
                AudioSentimentResult, "model_dump", return_value=result_dict
            ):
                response = client.get("/api/audio_analysis/test-job-id/result")
                assert response.status_code == 200


def test_get_audio_analysis_result_not_finished():
    """Test getting the result of a job that's not finished yet"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = False
    mock_job.is_started = True

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Force exception to be raised with the expected message
            with patch(
                "routes.audio_analysis.HTTPException",
                side_effect=lambda **kwargs: Exception(kwargs["detail"]),
            ):
                # Make sure the endpoint gets the actual function call
                with pytest.raises(Exception) as excinfo:
                    client.get("/api/audio_analysis/test-job-id/result")
                assert "Job is still processing" in str(excinfo.value)


def test_get_audio_analysis_result_failed():
    """Test getting the result of a failed job"""
    mock_job = MagicMock()
    mock_job.is_finished = False
    mock_job.is_failed = True
    mock_job.exc_info = "Test error"

    with patch("rq.job.Job.fetch", return_value=mock_job):
        with patch("redisStore.myconnection.get_redis_con"):
            # Force exception to be raised with the expected message
            with patch(
                "routes.audio_analysis.HTTPException",
                side_effect=lambda **kwargs: Exception(kwargs["detail"]),
            ):
                # Make sure the endpoint gets the actual function call
                with pytest.raises(Exception) as excinfo:
                    client.get("/api/audio_analysis/test-job-id/result")
                assert "Test error" in str(excinfo.value)
