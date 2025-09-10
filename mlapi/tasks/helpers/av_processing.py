from utils.logger_config import get_logger
from schemas.create_answer import (
    TimelineStructure,
    EmotionDetectionResult,
    AudioSentimentResult,
    SentimentResult,
    HighlightData,
)
from heapq import nlargest
from typing import List, Tuple, Dict, Any
import numpy as np

logger = get_logger(__name__)


def grab_top_five_keywords(audio_data: AudioSentimentResult) -> List[HighlightData]:
    """
    Extract the top five keywords from audio data.

    Args:
        audio_data: The audio analysis data from AssemblyAI

    Returns:
        List[HighlightData]: Top five keywords by rank
    """
    keywords = audio_data.highlights
    top_five = nlargest(5, keywords, key=lambda item: item.rank)
    return top_five


def calculate_overall_audio_sentiment(audio_data: AudioSentimentResult) -> str:
    """
    Calculate the most common sentiment in the audio data.

    Args:
        audio_data: The audio analysis data from AssemblyAI

    Returns:
        str: The most common sentiment (POSITIVE, NEGATIVE, or NEUTRAL)
    """
    sentiments = audio_data.sentiment_analysis
    sent_list = [i.sentiment for i in sentiments]

    if not sent_list:
        return "NEUTRAL"

    counted_sents = max(set(sent_list), key=sent_list.count) if sent_list else "NEUTRAL"
    return counted_sents


def _build_timeline_intervals_sentiment(
    sent_analysis_lst: List[SentimentResult],
) -> List[List]:
    """
    Construct a timeline of sentiment intervals.

    Args:
        sent_analysis_lst: List of sentiment analysis results

    Returns:
        List[List]: List of [start_in_ms, end_in_ms, audio_sentiment_of_interval]
    """
    timeline = []
    for k in sent_analysis_lst:
        interval = [k.start, k.end, k.sentiment]
        timeline.append(interval)
    timeline.sort(key=lambda x: x[0])
    return timeline


def build_timeline_interval_facial(
    facial_data: EmotionDetectionResult,
) -> Dict[int, str]:
    """
    Build a facial emotion timeline.

    Args:
        facial_data: Facial emotion detection result

    Returns:
        Dict[int, str]: Dictionary mapping frame index to emotion
    """
    # Get all emotion timelines
    timelines = facial_data.timeline
    emotion_per_frame = []

    # Convert to dictionary form for each frame
    for i in range(facial_data.total_frames):
        frame_data = {}
        for emotion in timelines.__dict__:
            timeline = getattr(timelines, emotion)
            if i < len(timeline):
                frame_data[emotion] = timeline[i]
            else:
                frame_data[emotion] = 0.0

        # Find emotion with maximum value for this frame
        if frame_data:
            max_emotion = max(frame_data.items(), key=lambda x: x[1])[0]
            emotion_per_frame.append(max_emotion)

    # Create a dictionary mapping frame index to emotion
    facial_timeline = {
        k: v for k, v in zip(list(range(len(emotion_per_frame))), emotion_per_frame)
    }
    return facial_timeline


def _emotion_sentiment_match(
    start: int, end: int, interval_length: int, facial_timeline: Dict[int, str]
) -> List[str]:
    """
    Match facial emotions to a given audio time segment.

    Args:
        start: Start time in milliseconds
        end: End time in milliseconds
        interval_length: Frame interval length in milliseconds
        facial_timeline: Dictionary mapping frame index to emotion

    Returns:
        List[str]: Facial emotions for the given time segment
    """
    try:
        return [
            facial_timeline[start // interval_length],
            facial_timeline[end // interval_length],
        ]
    except Exception as e:
        logger.error(f"Error in sentiment matching: {str(e)}")
        logger.error(f"Facial timeline: {facial_timeline}")
        logger.error(
            f"Parameters: start={start}, end={end}, interval_length={interval_length}"
        )
        logger.error(
            f"Calculations: start//interval={start // interval_length}, end//interval={end // interval_length}"
        )
        return ["neutral", "neutral"]  # Default fallback


def av_timeline_resolution(
    clip_length: float,
    facial_data: EmotionDetectionResult,
    audio_sentiments: List[SentimentResult],
) -> List[TimelineStructure]:
    """
    Create a timeline of audio-visual data.

    Args:
        clip_length: Video/audio length in seconds
        facial_data: Facial emotion detection results
        audio_sentiments: Audio sentiment analysis results

    Returns:
        List[TimelineStructure]: Combined timeline of audio and facial data
    """
    if facial_data.total_frames == 0 or not audio_sentiments:
        logger.warning("Invalid facial data or audio sentiments")
        return []

    total_frames = facial_data.total_frames
    fps = round(total_frames / clip_length) if clip_length > 0 else 30
    interval_length = 1000 // fps  # milliseconds per frame

    audio_timeline = _build_timeline_intervals_sentiment(audio_sentiments)
    facial_timeline = build_timeline_interval_facial(facial_data)

    timeline = []
    for stats in audio_timeline:
        entry = TimelineStructure(
            start=stats[0],
            end=stats[1],
            audioSentiment=stats[2],
            facialEmotion=_emotion_sentiment_match(
                stats[0], stats[1], interval_length, facial_timeline
            ),
        )
        timeline.append(entry)

    # Filter out entries with invalid facial emotions
    timeline = [t for t in timeline if t.facialEmotion != ["neutral", "neutral"]]
    return timeline


def calculate_top_three_facial_with_count(
    facial_data: EmotionDetectionResult,
) -> Tuple[List[str], float, float, float]:
    """
    Calculate the top three emotions and their frequencies.

    Args:
        facial_data: Facial emotion detection results

    Returns:
        Tuple: (top_three_emotions, frequency_top, frequency_second, frequency_third)
    """
    timeline_interval = build_timeline_interval_facial(facial_data)
    emotions_per_interval = list(timeline_interval.values())

    if not emotions_per_interval:
        return ["neutral", "neutral", "neutral"], 1.0, 0.0, 0.0

    # Count occurrences of each emotion
    fdist = dict(zip(*np.unique(emotions_per_interval, return_counts=True)))

    # Get top three emotions
    top_three = sorted(fdist, key=lambda k: int(fdist[k]), reverse=True)[:3]

    # Pad with N/A if less than three emotions detected
    if len(top_three) < 3:
        iterations = 3 - len(top_three)
        for _ in range(iterations):
            top_three.append("neutral")
        fdist["neutral"] = 0.0

    # Calculate frequencies
    top_three_with_count = [
        (top_three[0], fdist[top_three[0]]),
        (top_three[1], fdist[top_three[1]]),
        (top_three[2], fdist[top_three[2]]),
    ]

    denominator = (
        top_three_with_count[0][1]
        + top_three_with_count[1][1]
        + top_three_with_count[2][1]
    )

    if denominator == 0:
        return top_three, 0.0, 0.0, 0.0

    top_stat = round(float(top_three_with_count[0][1] / denominator), 2)
    second_stat = round(float(top_three_with_count[1][1] / denominator), 2)
    third_stat = round(float(top_three_with_count[2][1] / denominator), 2)

    # Convert to string for consistency
    top_three = [str(i) for i in top_three]

    return top_three, top_stat, second_stat, third_stat
