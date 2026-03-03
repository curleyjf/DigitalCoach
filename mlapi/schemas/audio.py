# Audio analysis schemas for sentiment, highlights, and IAB categories
from enum import Enum
from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from schemas.jobs import JobStatus

class ASM_Sentiments(str, Enum):
    """
    Audio sentiments detected by AssemblyAI
    """

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"

class SentimentResult(BaseModel):
    """Individual sentiment analysis result for a text segment"""

    text: str
    sentiment: str  # "POSITIVE", "NEUTRAL", or "NEGATIVE"
    confidence: float  # Confidence score 0.0-1.0
    start: int  # Start time in milliseconds
    end: int  # End time in milliseconds

class TimestampData(BaseModel):
    """Timestamp info for keyword occurrences"""

    start: int  # Start time in milliseconds
    end: int  # End time in milliseconds


class HighlightData(BaseModel):
    """Data for auto-highlighted keywords/phrases"""

    text: str  # The highlighted word or phrase
    rank: float  # Importance ranking (0-1), words relevant to the content.
    count: int  # Number of occurrences
    timestamps: List[TimestampData] = Field(default_factory=list)

class IABLabel(BaseModel):
    """IAB category label with relevance score from AssemblyAI"""

    label: str  # Category name
    relevance: float  # Relevance score (0-1)


class IABResult(BaseModel):
    """IAB category detection results from AssemblyAI"""

    text: str = ""  # Input text that was analyzed
    labels: List[IABLabel] = Field(default_factory=list)  # Detected category labels

class AudioSentimentResult(BaseModel):
    """
    Result of audio sentiment analysis by AssemblyAI
    """

    sentiment_analysis: List[SentimentResult] = Field(default_factory=list)
    highlights: List[HighlightData] = Field(default_factory=list)
    iab_results: IABResult = Field(default_factory=IABResult)
    clip_length_seconds: float = 0.0
    errors: Optional[str] = None

class AudioAnalysisResponse(BaseModel):
    """
    Response model for audio analysis job
    """

    job_id: str
    status: JobStatus
    result: AudioSentimentResult | None = None
    error: str | None = None


class ExtractedAudio(BaseModel):
    """
    Result of audio extraction by MoviePy
    """

    path_to_file: str
    clip_length_seconds: float

class AudioAnalysisRequest(BaseModel):
    """
    Request to start an audio analysis job
    
    Args: 
        video_url: The URL of the video to analyze
    Returns:
        AudioAnalysisRequest: The request object
    Raises:
        ValidationError: If the video_url is empty or not a valid URL
    """

    video_url: HttpUrl = Field(...,description="URL to analyze")