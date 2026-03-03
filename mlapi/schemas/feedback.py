"""
User's Performance Feedback Schemas
"""

from pydantic import BaseModel, Field
from typing import List
from schemas.jobs import JobStatus

class BigFiveScoreResult(BaseModel):
    """
    Big Five Score Analysis
    """

    o: float = Field(..., description="Openness score", ge=0, le=100)
    c: float = Field(..., description="Conscientiousness score", ge=0, le=100)
    e: float = Field(..., description="Extraversion score", ge=0, le=100)
    a: float = Field(..., description="Agreeableness score", ge=0, le=100)
    n: float = Field(..., description="Neuroticism score", ge=0, le=100)
    _disclaimer: str | None = None # Optional Disclaimer about score interpretation

class BigFiveRequest(BaseModel):
    """
    Request model for Big Five scores
    """

    o: float = Field(..., description="Openness score", ge=0, le=100)
    c: float = Field(..., description="Conscientiousness score", ge=0, le=100)
    e: float = Field(..., description="Extraversion score", ge=0, le=100)
    a: float = Field(..., description="Agreeableness score", ge=0, le=100)
    n: float = Field(..., description="Neuroticism score", ge=0, le=100)


class BigFiveResponse(BaseModel):
    """
    Response model for Big Five scores with feedback
    """

    feedback: List[str]

class CompetencyFeedback(BaseModel):
    """
    Feedback for a specific competency
    """

    score: float # Overall score
    strengths: List[str] = Field(default_factory=list) # List of strengths displayed in interview
    areas_for_improvement: List[str] = Field(default_factory=list) # List of areas to improve
    recommendations: List[str] = Field(default_factory=list) # Recommended course of action

class OverallCompetencyFeedback(BaseModel):
    """
    Overall Competency Feedback
    """

    communication_clarity: CompetencyFeedback  # Feedback on communication clarity
    confidence: CompetencyFeedback # Feedback on confidence
    engagement: CompetencyFeedback # Feedback on engagement
    overall_score: float # Overall sscore
    summary: str # Summary of overall performance
    key_recommendations: List[str] = Field(default_factory=list) # Specific actions to take

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

class StarFeedbackRequest(BaseModel):
    """
    Request model for STAR feedback
    """
    
    text: str

class StarClassification(BaseModel):
    """
    Classification result for a single sentence
    """

    sentence: str
    category: str


class StarPercentages(BaseModel):
    """
    Percentage breakdown of STAR components
    """

    action: float
    result: float
    situation: float
    task: float


class StarFeedbackEvaluation(BaseModel):
    """
    Results after performing STAR feedback analysis
    """

    fulfilled_star: bool
    percentages: StarPercentages
    classifications: List[StarClassification]
    feedback: List[str]

class StarFeedbackResponse(BaseModel):
    """
    Response model for STAR feedback job
    """

    job_id: str
    status: JobStatus
    result: StarFeedbackEvaluation | None = None
    error: str | None = None