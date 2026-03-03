from tasks.helpers.constants import (
    FACIAL_EMOTION_POINTS,
    AV_ASSOCIATIONS,
    OVERALL_AUDIO_POINTS,
    OVERAL_FACIAL_POINTS,
    AUDIO_EMOTION_POINTS,
)
import re
from schemas.create_answer import (
    # TextStructureResult,
    # AudioSentimentResult,
    # StructureDetails,
    BigFiveScoreResult,
    CreateAnswerEvaluation,
)
from tasks.helpers.analyze_text_structure_ml import analyze_text_structure_ml
from tasks.helpers.text_preprocessing import clean_text
from tasks.helpers.av_processing import (
    calculate_overall_audio_sentiment,
    grab_top_five_keywords,
)
from typing import Tuple, List
from utils.logger_config import get_logger

logger = get_logger(__name__)


def _compute_av_sentiment_matches(timeline) -> float:
    """
    Calculate points for audio-visual sentiment matches.

    Args:
        timeline: The timeline of the video

    Returns:
        float: The percentage of matches between the audio and visual sentiment
    """
    total_pts = len(timeline) * 2
    if total_pts == 0:
        return 0

    pts = 0
    for entry in timeline:
        facial_emotions = entry.facialEmotion
        audio_sentiment = entry.audioSentiment

        if len(facial_emotions) < 2:
            continue

        if (
            facial_emotions[0] in AV_ASSOCIATIONS[audio_sentiment]
            and facial_emotions[1] in AV_ASSOCIATIONS[audio_sentiment]
        ):
            pts += 2
        elif (
            facial_emotions[0] in AV_ASSOCIATIONS[audio_sentiment]
            and facial_emotions[1] not in AV_ASSOCIATIONS[audio_sentiment]
        ):
            pts += 1
        elif (
            facial_emotions[0] not in AV_ASSOCIATIONS[audio_sentiment]
            and facial_emotions[1] in AV_ASSOCIATIONS[audio_sentiment]
        ):
            pts += 1

    av_matches = (pts / total_pts) * 10
    return av_matches


def _compute_pts_for_emotion_occurences(timeline) -> float:
    """
    Calculate points for emotional expression variety.

    Args:
        timeline: The timeline of the video

    Returns:
        float: The percentage of the total points earned
    """
    total_pts = len(timeline) * 6
    if total_pts == 0:
        return 0

    pts = 0
    for entry in timeline:
        facial_emotions = entry.facialEmotion
        audio_sentiment = entry.audioSentiment

        pts += AUDIO_EMOTION_POINTS.get(audio_sentiment, 0)

        if len(facial_emotions) >= 2:
            pts += FACIAL_EMOTION_POINTS.get(
                facial_emotions[0], 0
            ) + FACIAL_EMOTION_POINTS.get(facial_emotions[1], 0)

    if pts <= 0:
        return 0

    return (pts / total_pts) * 10


def compute_aggregate_score(result: CreateAnswerEvaluation) -> float:
    """
    Compute aggregate score from various metrics.

    Args:
        result: The evaluation result

    Returns:
        float: The aggregate score
    """
    text_structure_score = result.predictionScore
    overall_facial = OVERAL_FACIAL_POINTS.get(result.overallFacialEmotion, 0)
    overall_audio = OVERALL_AUDIO_POINTS.get(result.overallSentiment, 0)

    # Safely compute values that could fail
    av_matches = 5.0  # Default value
    emotion_occurences = 6.0  # Default value

    if result.timeline:
        try:
            av_matches = round(_compute_av_sentiment_matches(result.timeline), 2)
            emotion_occurences = round(
                _compute_pts_for_emotion_occurences(result.timeline), 2
            )
        except Exception as e:
            logger.error(f"Error computing timeline scores: {str(e)}")

    logger.info(
        f"COMPUTING AGGREGATE SCORE: text structure score: {text_structure_score}"
    )
    logger.info(f"COMPUTING AGGREGATE SCORE: overall facial score: {overall_facial}")
    logger.info(f"COMPUTING AGGREGATE SCORE: overall audio score: {overall_audio}")
    logger.info(f"COMPUTING AGGREGATE SCORE: av_matches: {av_matches}")
    logger.info(f"COMPUTING AGGREGATE SCORE: emotion_occurences: {emotion_occurences}")

    aggregate = (
        text_structure_score
        + overall_facial
        + overall_audio
        + av_matches
        + emotion_occurences
    )
    return round(aggregate, 2)


def score_text_structure(audio_answer: AudioSentimentResult) -> TextStructureResult:
    """
    Score how structured the user's answers are using a hybrid approach:
    1. Rule-based analysis for basic structure indicators
    2. Optional pre-trained model integration (if configured)

    Args:
        audio_answer: The audio sentiment analysis result

    Returns:
        TextStructureResult: Text structure analysis result
    """
    # Extract text from sentiment analysis if available
    text = ""
    if audio_answer.sentiment_analysis:
        for sentiment in audio_answer.sentiment_analysis:
            text += sentiment.text

    # Default to a minimal text if no content is available
    if not text:
        text = "No transcript available"

    cleaned_text: str = clean_text(answer=text)
    structure_score, structure_details = _analyze_text_structure(text=cleaned_text)
    binary_prediction = 1 if structure_score >= 50 else 0

    return TextStructureResult(
        prediction_score=structure_score,
        binary_prediction=binary_prediction,
        output_text=cleaned_text,
        details=structure_details,
    )


def _analyze_text_structure(text: str) -> Tuple[float, StructureDetails]:
    """
    Analyzes text structure using rule-based heuristics.

    Args:
        text: The text to analyze

    Returns:
        tuple containing:
        - float: Structure score (0-100)
        - StructureDetails: Detailed breakdown of structure components
    """
    # Initialize structure metrics
    metrics = StructureDetails(
        paragraph_count=0,
        avg_paragraph_length=0,
        transition_words=0,
        has_intro=False,
        has_conclusion=False,
        sentence_variety=0,
    )

    # Split into paragraphs
    paragraphs = re.split(r"\n\s*\n|\r\n\s*\r\n", text)
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    metrics.paragraph_count = len(paragraphs)

    # Calculate average paragraph length
    if metrics.paragraph_count > 0:
        total_sentences = 0
        for p in paragraphs:
            sentences = re.split(r"[.!?]+", p)
            sentences = [s.strip() for s in sentences if s.strip()]
            total_sentences += len(sentences)
        metrics.avg_paragraph_length = (
            total_sentences // metrics.paragraph_count
            if metrics.paragraph_count > 0
            else 0
        )

    # Check for transition words/phrases
    transition_words = [
        "first",
        "second",
        "third",
        "finally",
        "consequently",
        "in conclusion",
        "for example",
        "moreover",
        "however",
        "therefore",
        "in addition",
        "furthermore",
        "thus",
        "meanwhile",
        "nevertheless",
        "subsequently",
    ]
    lower_text = text.lower()
    for word in transition_words:
        if word in lower_text:
            metrics.transition_words += 1

    # Check for introduction and conclusion
    intro_patterns = ["introduce", "begin", "start", "first", "today", "topic"]
    conclusion_patterns = [
        "conclude",
        "conclusion",
        "summary",
        "finally",
        "in summary",
        "to sum up",
    ]

    # Check first and last paragraphs
    first_para = paragraphs[0].lower() if paragraphs else ""
    last_para = paragraphs[-1].lower() if paragraphs else ""
    metrics.has_intro = any(pattern in first_para for pattern in intro_patterns)
    metrics.has_conclusion = any(
        pattern in last_para for pattern in conclusion_patterns
    )

    # Calculate overall structure score (weighted components)
    score = 0

    # Good paragraph structure (3-5 paragraphs ideal)
    if 3 <= metrics.paragraph_count <= 5:
        score += 30
    elif metrics.paragraph_count > 1:
        score += 15

    # Good paragraph length (2-5 sentences per paragraph)
    if 2 <= metrics.avg_paragraph_length <= 5:
        score += 15
    elif metrics.avg_paragraph_length > 0:
        score += 5

    # Has transition words
    score += min(20, metrics.transition_words * 5)

    # Has intro
    if metrics.has_intro:
        score += 15

    # Has conclusion
    if metrics.has_conclusion:
        score += 20

    # Ensure score is between 0-100
    calculate_score = max(min(score, 100), 0)

    # ML model feedback
    ml_score, _ = analyze_text_structure_ml(text)

    # weighted average
    final_score = (calculate_score + ml_score) / 2
    return final_score, metrics


def score_bigFive(
    audio_answer: AudioSentimentResult,
    facial_stats: List[str],
    text_answer: TextStructureResult,
) -> BigFiveScoreResult:
    """
    Attempts to approximate Big Five personality traits on a scale of 0-7.

    Args:
        audio_answer: Audio sentiment analysis result
        facial_stats: Facial emotion statistics
        text_answer: Text structure analysis result

    Returns:
        BigFiveScoreResult: Big Five personality trait scores
    """
    # Default base scores (neutral starting points at middle of scale)
    o_score, c_score, e_score, a_score, n_score = 3.5, 3.5, 3.5, 3.5, 3.5

    # Get relevant signals from the analysis if available
    sentiment_score = 0
    overall_sentiment = calculate_overall_audio_sentiment(audio_answer)
    if overall_sentiment == "POSITIVE":
        sentiment_score = 1
    elif overall_sentiment == "NEGATIVE":
        sentiment_score = -1
    elif overall_sentiment == "NEUTRAL":
        sentiment_score = -0.5

    # Adjust scores based on keyword complexity (weak signal)
    keywords = grab_top_five_keywords(audio_answer) if audio_answer else []
    avg_keyword_length = 0
    if keywords:
        avg_keyword_length = sum(min(len(kw.text), 10) for kw in keywords) / max(
            len(keywords), 1
        )
        o_score += (avg_keyword_length - 5) / 5 * 2  # Scale adjusted for 0-7 range

    # Facial expression adjustments (weak signal)
    if facial_stats and len(facial_stats) > 0:
        top_emotion = facial_stats[0]
        if top_emotion == "happy":
            e_score += 1
            a_score += 1
            n_score -= 0.5
        elif top_emotion == "neutral":
            pass
        elif top_emotion in ["sad", "fear", "disgust", "angry"]:
            n_score += 1
            e_score -= 0.5
            a_score -= 0.5

    # Adjust based on text structure if available
    if text_answer:
        structure_score = text_answer.prediction_score / 100
        c_score += (structure_score - 0.5) * 2  # normalized to roughly -1 to 1

    # Sentiment affects extraversion, agreeableness, and neuroticism
    e_score += sentiment_score
    a_score += sentiment_score * 0.5
    n_score -= sentiment_score * 0.5

    # Final normalization to ensure scores are within 0-7 scale
    def normalize_score(score):
        return max(min(round(score * 10) / 10, 7), 0)

    return BigFiveScoreResult(
        o=normalize_score(o_score),
        c=normalize_score(c_score),
        e=normalize_score(e_score),
        a=normalize_score(a_score),
        n=normalize_score(n_score),
        _disclaimer="This is a weak approximation of Big Five traits and should not be used for serious assessments.",
    )
