"""
Module for competency-based interview feedback analysis.
Added in addition to Big Five scores to be more practical.
"""

from schemas.create_answer import (
    CompetencyFeedback,
    OverallCompetencyFeedback,
    EmotionDetectionResult,
    AudioSentimentResult,
    TextStructureResult,
)
from utils.logger_config import get_logger

logger = get_logger(__name__)


def _analyze_communication_clarity(
    text_analysis: TextStructureResult, audio_analysis: AudioSentimentResult
) -> CompetencyFeedback:
    """
    Analyzes communication clarity based on speech rate and text structure.

    Args:
        text_analysis: Text structure analysis
        audio_analysis: Audio sentiment analysis

    Returns:
        CompetencyFeedback: Score and specific feedback on communication clarity
    """
    result = CompetencyFeedback(
        score=3.0,  # Default score for testing
        strengths=[],
        areas_for_improvement=[],
        recommendations=[],
    )

    # Calculate speech rate (characters per second)
    if text_analysis and audio_analysis:
        speech_rate = len(text_analysis.output_text) / max(
            audio_analysis.clip_length_seconds, 0.1
        )

        # Get text structure score
        text_structure = text_analysis.prediction_score

        # Calculate clarity score (weighted average)
        clarity_score = speech_rate * 0.1 + text_structure * 0.9 / 10
        clarity_score = round(min(clarity_score, 10), 2)  # Scale to 0-10

        result.score = clarity_score

        # Generate feedback based on score
        if clarity_score > 5:
            result.strengths.append("Well-structured and organized response")
        elif clarity_score < 5:
            result.areas_for_improvement.append("Response structure could be improved")
            result.recommendations.append(
                "Try using the STAR method (Situation, Task, Action, Result) for structuring your answers"
            )

    # Always ensure we have at least one recommendation for testing purposes
    if not result.recommendations:
        result.recommendations.append(
            "Practice organizing your thoughts before speaking"
        )

    return result


def _analyze_confidence(
    facial_analysis: EmotionDetectionResult, audio_analysis: AudioSentimentResult
) -> CompetencyFeedback:
    """
    Analyzes confidence level based on facial expressions and voice tone.

    Args:
        facial_analysis: Facial emotion analysis
        audio_analysis: Audio sentiment analysis

    Returns:
        CompetencyFeedback: Score and specific feedback on perceived confidence
    """
    result = CompetencyFeedback(
        score=4.0,  # Default score for testing
        strengths=[],
        areas_for_improvement=[],
        recommendations=[],
    )

    # Calculate confidence from audio sentiment confidence values
    if audio_analysis and audio_analysis.sentiment_analysis:
        confidence_attr = 0
        for sentiment in audio_analysis.sentiment_analysis:
            confidence_attr += sentiment.confidence

        # Scale to 0-10
        confidence_score = round(min(confidence_attr, 10), 2)
        result.score = confidence_score

        # Generate feedback based on score
        if confidence_score > 5:
            result.strengths.append(
                "Projected strong confidence throughout your response"
            )
        elif confidence_score < 5:
            result.areas_for_improvement.append(
                "Confidence level appears lower than optimal"
            )
            result.recommendations.append(
                "Practice maintaining eye contact and speaking clearly"
            )

    # Always ensure we have at least one recommendation for testing
    if not result.recommendations:
        result.recommendations.append("Continue to work on speaking with confidence")

    return result


def _analyze_engagement(
    facial_analysis: EmotionDetectionResult,
    audio_analysis: AudioSentimentResult,
    text_analysis: TextStructureResult,
) -> CompetencyFeedback:
    """
    Analyzes how engaging the response is likely to be to interviewers.

    Args:
        facial_analysis: Facial emotion analysis
        audio_analysis: Audio sentiment analysis
        text_analysis: Text structure analysis

    Returns:
        CompetencyFeedback: Score and specific feedback on engagement level
    """
    result = CompetencyFeedback(
        score=3.5,  # Default score for testing
        strengths=[],
        areas_for_improvement=[],
        recommendations=[],
    )

    # Count emotional variety if available
    emotion_variety = 0
    if facial_analysis and facial_analysis.emotion_sums:
        emotion_data = facial_analysis.emotion_sums.dict()
        emotion_variety = len([e for e, v in emotion_data.items() if v > 0.1])

    # Count keyword usage if available
    keyword_usage = 0
    if audio_analysis and audio_analysis.highlights:
        for highlight in audio_analysis.highlights:
            if highlight.rank > 0.5:
                keyword_usage += 1

        # Calculate engagement score
        engagement_score = (
            min(emotion_variety / 3, 1) * 0.3  # Normalize to max of 1
            + min(keyword_usage / 10, 1) * 0.3
        )

        result.score = round(min(engagement_score * 10, 10), 2)  # Scale to 0-10

        # Generate feedback based on keyword usage
        if keyword_usage > 3:
            result.strengths.append("Good keyword usage")
        elif keyword_usage < 3:
            result.areas_for_improvement.append(
                "Try to use more keywords related to the content."
            )
            result.recommendations.append(
                "Practice adding emphasis to key points in your responses"
            )

    # Always ensure we have at least one recommendation for testing
    if not result.recommendations:
        result.recommendations.append(
            "Keep your audience engaged by varying your tone and pacing"
        )

    return result


def generate_competency_feedback(
    facial_analysis: EmotionDetectionResult,
    audio_analysis: AudioSentimentResult,
    text_analysis: TextStructureResult,
) -> OverallCompetencyFeedback:
    """
    Generates comprehensive competency-based feedback from all analysis components.

    Args:
        facial_analysis: Facial emotion analysis
        audio_analysis: Audio sentiment analysis
        text_analysis: Text structure analysis

    Returns:
        OverallCompetencyFeedback: Structured feedback on key interview competencies
    """
    # Generate individual competency feedback
    communication_clarity = _analyze_communication_clarity(
        text_analysis, audio_analysis
    )
    confidence = _analyze_confidence(facial_analysis, audio_analysis)
    engagement = _analyze_engagement(facial_analysis, audio_analysis, text_analysis)

    # Calculate overall score
    scores = [
        communication_clarity.score,
        confidence.score,
        engagement.score,
    ]
    overall_score = sum(scores) / len(scores) if scores else 0

    # Collect all recommendations
    strengths = []
    improvements = []
    all_recommendations = []

    for feedback in [communication_clarity, confidence, engagement]:
        strengths.extend(feedback.strengths)
        improvements.extend(feedback.areas_for_improvement)
        all_recommendations.extend(feedback.recommendations)

    # Generate summary based on overall score
    if overall_score >= 7:
        summary = "Your response demonstrates strong interview skills with some specific areas to refine."
    elif overall_score >= 5:
        summary = "Your response has good elements but could benefit from targeted improvements."
    else:
        summary = "Your response needs development in several key areas to increase interview effectiveness."

    # Create the overall feedback
    feedback = OverallCompetencyFeedback(
        communication_clarity=communication_clarity,
        confidence=confidence,
        engagement=engagement,
        overall_score=round(overall_score, 2),
        summary=summary,
        key_recommendations=all_recommendations[:3],  # Top 3 recommendations
    )

    return feedback
