from schemas.create_answer import (
    AudioSentimentResult,
    SentimentResult,
    HighlightData,
    TimestampData,
    IABLabel,
)
from typing import List
import assemblyai as aai
from utils.logger_config import get_logger
from rq.decorators import job
from redisStore.myconnection import get_redis_con
import os

AAPI_KEY = os.getenv("AAPI_KEY")
logger = get_logger(__name__)


@job("high", connection=get_redis_con())
def detect_audio_sentiment(video_url: str) -> AudioSentimentResult:
    """
    Detects audio sentiment using the AssemblyAI API package

    Args:
        video_url: URL or path to the audio/video file

    Returns:
        AudioSentimentResult: Sentiment analysis results
    """
    result = AudioSentimentResult()

    try:
        # Initialize the AssemblyAI client
        if not AAPI_KEY:
            logger.error("No AssemblyAI API key found in environment")
            result.errors = "No AssemblyAI API key configured"
            return result

        aai.settings.api_key = AAPI_KEY
        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
            sentiment_analysis=True,
            auto_highlights=True,
            iab_categories=True,
        )

        logger.info(f"Transcribing audio file: {video_url}")
        transcript: aai.Transcript = transcriber.transcribe(
            video_url,
            config,
        )

        if transcript.error:
            raise Exception(transcript.error)

        # Process sentiment analysis results
        if transcript.sentiment_analysis:
            sentiment_results: List[SentimentResult] = []
            for analysis in transcript.sentiment_analysis:
                sentiment_results.append(
                    SentimentResult(
                        text=analysis.text,
                        sentiment=analysis.sentiment.value,
                        confidence=analysis.confidence,
                        start=analysis.start,
                        end=analysis.end,
                    )
                )
            result.sentiment_analysis = sentiment_results

        # Process auto highlights (key phrases)
        if transcript.auto_highlights and transcript.auto_highlights.results:
            highlight_results: List[HighlightData] = []
            for highlight in transcript.auto_highlights.results:
                timestamps = [
                    TimestampData(start=ts.start, end=ts.end)
                    for ts in highlight.timestamps
                ]
                highlight_results.append(
                    HighlightData(
                        text=highlight.text,
                        rank=highlight.rank,
                        count=highlight.count,
                        timestamps=timestamps,
                    )
                )
            result.highlights = highlight_results

        # Process IAB categories (topic detection)
        try:
            categories = transcript.iab_categories
            if categories is not None:
                results = getattr(categories, "results", None)
                if results and isinstance(results, (list, tuple)) and len(results) > 0:
                    first_result = results[0]
                    if hasattr(first_result, "text") and hasattr(
                        first_result, "labels"
                    ):
                        result.iab_results.text = str(first_result.text)

                        labels = getattr(first_result, "labels", None)
                        if labels and isinstance(labels, (list, tuple)):
                            result.iab_results.labels = [
                                IABLabel(
                                    label=str(getattr(label, "label", "")),
                                    relevance=float(getattr(label, "relevance", 0.0)),
                                )
                                for label in labels
                                if hasattr(label, "label")
                                and hasattr(label, "relevance")
                            ]
        except Exception as e:
            logger.warning(f"Failed to process IAB categories: {str(e)}")

        # Set clip length if available
        if hasattr(transcript, "audio_duration"):
            result.clip_length_seconds = (
                transcript.audio_duration / 1000.0
            )  # Convert ms to seconds

        logger.info(f"Transcript processing completed for {video_url}")
        logger.info(f"transcript: {transcript.text}")

    except Exception as e:
        logger.error(f"Exception in audio sentiment detection: {str(e)}")
        result.errors = str(e)

    return result
