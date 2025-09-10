from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class FER_Emotions(str, Enum):
    """
    Facial emotions detected by DeepFace
    """

    ANGRY = "angry"
    DISGUST = "disgust"
    FEAR = "fear"
    HAPPY = "happy"
    SAD = "sad"
    SURPRISE = "surprise"
    NEUTRAL = "neutral"


class ASM_Sentiments(str, Enum):
    """
    Audio sentiments detected by AssemblyAI
    """

    POSITIVE = "POSITIVE"
    NEGATIVE = "NEGATIVE"
    NEUTRAL = "NEUTRAL"


class EmotionTotals(BaseModel):
    angry: float = 0.0
    disgust: float = 0.0
    fear: float = 0.0
    happy: float = 0.0
    sad: float = 0.0
    surprise: float = 0.0
    neutral: float = 0.0


class EmotionTimelines(BaseModel):
    angry: List[float] = Field(default_factory=list)
    disgust: List[float] = Field(default_factory=list)
    fear: List[float] = Field(default_factory=list)
    happy: List[float] = Field(default_factory=list)
    sad: List[float] = Field(default_factory=list)
    surprise: List[float] = Field(default_factory=list)
    neutral: List[float] = Field(default_factory=list)


class EmotionDetectionResult(BaseModel):
    """
    Result of facial emotion detection processing by DeepFace
    """

    total_frames: int = 0  # Total number of frames analyzed
    frame_inference_rate: int = 30  # Frequency of frame sampling
    emotion_sums: EmotionTotals = Field(default_factory=EmotionTotals)
    timeline: EmotionTimelines = Field(default_factory=EmotionTimelines)
    clip_length_seconds: float = 0.0  # Audio duration in seconds
    errors: Optional[str] = None
    avg_inference_time: Optional[float] = None


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
    """IAB category label with relevance score"""

    label: str  # Category name
    relevance: float  # Relevance score (0-1)


class IABResult(BaseModel):
    """IAB category detection results"""

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


class ExtractedAudio(BaseModel):
    """
    Result of audio extraction by MoviePy
    """

    path_to_file: str
    clip_length_seconds: float


class Content(BaseModel):
    """
    Content to be processed by `create_answer`
    """

    fname: str  # Full path to the video file
    rename: str  # Filename to be used for audio file


class StructureDetails(BaseModel):
    """
    Metrics for text structure analysis
    """

    paragraph_count: int = 0
    avg_paragraph_length: int = 0
    transition_words: int = 0
    has_intro: bool = False
    has_conclusion: bool = False
    sentence_variety: int = 0


class TextStructureResult(BaseModel):
    """
    Text Structure Analysis
    """

    prediction_score: float
    binary_prediction: int
    output_text: str
    details: StructureDetails = Field(default_factory=StructureDetails)


class TimelineStructure(BaseModel):
    """
    Timeline Structure Analysis
    """

    start: int  # in milliseconds
    end: int  # in milliseconds
    audioSentiment: str
    facialEmotion: List[str] = Field(default_factory=list)


class BigFiveScoreResult(BaseModel):
    """
    Big Five Score Analysis
    """

    o: float
    c: float
    e: float
    a: float
    n: float
    _disclaimer: str


class CompetencyFeedback(BaseModel):
    """
    Competency Feedback
    """

    score: float
    strengths: List[str] = Field(default_factory=list)
    areas_for_improvement: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class OverallCompetencyFeedback(BaseModel):
    """
    Overall Competency Feedback
    """

    communication_clarity: CompetencyFeedback
    confidence: CompetencyFeedback
    engagement: CompetencyFeedback
    overall_score: float
    summary: str
    key_recommendations: List[str] = Field(default_factory=list)


class FacialStatistics(BaseModel):
    """
    Facial emotion statistics
    """

    topThreeEmotions: List[str] = Field(default_factory=list)
    frequencyOfTopEmotion: float = 0.0
    frequencyOfSecondEmotion: float = 0.0
    frequencyOfThirdEmotion: float = 0.0


class CreateAnswerEvaluation(BaseModel):
    """
    Result of creating an answer
    """

    timeline: List[TimelineStructure] = Field(default_factory=list)
    isStructured: int  # 1 or 0
    predictionScore: float  # 0-100
    facialStatistics: FacialStatistics
    overallFacialEmotion: str  # Most common facial emotion
    overallSentiment: str  # Overall audio sentiment from assemblyAI
    topFiveKeywords: List[HighlightData] = Field(default_factory=list)
    transcript: str  # Full transcript of speech
    bigFive: BigFiveScoreResult
    competencyFeedback: OverallCompetencyFeedback
    aggregateScore: float = 0.0  # Overall score (0-100)


class CreateAnswer(BaseModel):
    """
    Result of creating an answer
    """

    evaluation: CreateAnswerEvaluation


class JobStatus(str, Enum):
    """
    Status of a job
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AudioAnalysisJob(BaseModel):
    """
    AssemblyAI API job details
    """

    video_url: str
    job_id: str
    status: JobStatus = JobStatus.PENDING
    result: Optional[AudioSentimentResult] = None


class FacialAnalysisJob(BaseModel):
    """
    DeepFace analysis job details
    """

    video_url: str
    job_id: str
    status: JobStatus = JobStatus.PENDING
    result: Optional[EmotionDetectionResult] = None
