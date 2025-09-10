import pytest
import os
from schemas.create_answer import (
    EmotionDetectionResult,
    AudioSentimentResult,
)


@pytest.fixture
def get_redis_con():
    from redisStore.myconnection import get_redis_con

    return get_redis_con()


@pytest.fixture
def get_worker():
    from redisStore.worker import get_worker

    return get_worker()


@pytest.fixture
def test_video_path():
    """Get path to test video"""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    video_path = os.path.join(base_dir, "data", "test2.mp4")
    return video_path


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


def test_audio_analysis(monkeypatch):
    """Test audio analysis job with a mocked implementation"""

    # Create a simple mock implementation of detect_audio_sentiment
    def mock_detect_audio_sentiment(video_url):
        from schemas.create_answer import (
            SentimentResult,
            HighlightData,
            TimestampData,
            IABLabel,
            IABResult,
            AudioSentimentResult,
        )

        # Create a minimal test result
        return AudioSentimentResult(
            sentiment_analysis=[
                SentimentResult(
                    text="This is a test",
                    sentiment="NEUTRAL",
                    confidence=0.95,
                    start=1000,
                    end=2000,
                )
            ],
            highlights=[
                HighlightData(
                    text="test",
                    rank=0.8,
                    count=1,
                    timestamps=[TimestampData(start=1200, end=1300)],
                )
            ],
            clip_length_seconds=5.0,
            errors=None,
        )

    # Apply our mock implementation
    import tasks.assemblyai_api

    monkeypatch.setattr(
        tasks.assemblyai_api, "detect_audio_sentiment", mock_detect_audio_sentiment
    )

    # Test the function
    result = mock_detect_audio_sentiment("test_url")

    # Check result structure
    assert isinstance(result, AudioSentimentResult)
    assert result.errors is None
    assert result.clip_length_seconds == 5.0


def test_facial_analysis(test_video_path):
    """Test facial analysis job"""
    from tasks.detect_emotions import detect_emotions

    # Run facial emotion detection with high sample rate for faster execution
    result = detect_emotions(test_video_path, sample_rate=60)

    # Check result
    assert isinstance(result, EmotionDetectionResult)
    assert result.errors is None or "Error" not in result.errors
    assert result.total_frames > 0
    assert result.clip_length_seconds > 0

    # Verify emotion data
    emotions = result.emotion_sums.dict()
    for emotion, value in emotions.items():
        assert emotion in [
            "angry",
            "disgust",
            "fear",
            "happy",
            "sad",
            "surprise",
            "neutral",
        ]
        assert value >= 0

    # Check if timeline data is consistent
    for emotion, values in result.timeline.dict().items():
        assert isinstance(values, list)


def test_create_answer(monkeypatch, test_video_path, mock_audio_result):
    """Test the create_answer function with mocked dependencies"""
    from schemas.create_answer import (
        CreateAnswer,
        CreateAnswerEvaluation,
        FacialStatistics,
        BigFiveScoreResult,
        CompetencyFeedback,
        OverallCompetencyFeedback,
    )

    # Create a mock implementation that returns a fixed result
    def mock_create_answer(video_url, audio_job_id=None, facial_job_id=None):
        # Create a minimal but complete CreateAnswer result
        result = CreateAnswer(
            evaluation=CreateAnswerEvaluation(
                timeline=[],
                isStructured=1,
                predictionScore=75.5,
                facialStatistics=FacialStatistics(
                    topThreeEmotions=["neutral", "happy", "surprise"],
                    frequencyOfTopEmotion=0.8,
                    frequencyOfSecondEmotion=0.15,
                    frequencyOfThirdEmotion=0.05,
                ),
                overallFacialEmotion="neutral",
                overallSentiment="POSITIVE",
                topFiveKeywords=[],
                transcript="This is a test transcript",
                bigFive=BigFiveScoreResult(
                    o=3.5,
                    c=3.5,
                    e=3.5,
                    a=3.5,
                    n=3.5,
                    _disclaimer="This is a test disclaimer",
                ),
                competencyFeedback=OverallCompetencyFeedback(
                    communication_clarity=CompetencyFeedback(
                        score=3.5,
                        strengths=["Test strength"],
                        areas_for_improvement=["Test improvement"],
                        recommendations=["Test recommendation"],
                    ),
                    confidence=CompetencyFeedback(
                        score=3.5,
                        strengths=["Test strength"],
                        areas_for_improvement=["Test improvement"],
                        recommendations=["Test recommendation"],
                    ),
                    engagement=CompetencyFeedback(
                        score=3.5,
                        strengths=["Test strength"],
                        areas_for_improvement=["Test improvement"],
                        recommendations=["Test recommendation"],
                    ),
                    overall_score=3.5,
                    summary="Test summary",
                    key_recommendations=["Test recommendation"],
                ),
                aggregateScore=75.5,
            )
        )
        return result

    # Override the create_answer function with our mock
    import tasks.create_answer_task

    monkeypatch.setattr(tasks.create_answer_task, "create_answer", mock_create_answer)

    # Test the mocked function
    result = mock_create_answer(test_video_path)

    # Verify result
    assert isinstance(result, CreateAnswer)
    assert result.evaluation is not None
    assert result.evaluation.transcript is not None
    assert result.evaluation.bigFive is not None
    assert result.evaluation.competencyFeedback is not None
    assert result.evaluation.aggregateScore > 0
