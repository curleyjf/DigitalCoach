from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any, List
from enum import Enum


class JobStatus(str, Enum):
    """
    Status of a job
    """

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class JobId(BaseModel):
    """
    Job ID response model
    """

    job_id: str


class JobResponse(BaseModel):
    """
    Generic job response with status
    """

    job_id: str
    status: JobStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


class CreateAnswerJobRequest(BaseModel):
    """
    Request to create an answer job

    Args: 
        video_url: The URL of the video to analyze
    Returns:
        CreateAnswerJobRequest: The request object
    Raises:
        ValidationError: If the video_url is empty or not a valid URL
    """
    video_url: HttpUrl # URL of the video to analyze


class JobsListResponse(BaseModel):
    """
    Response model for listing jobs
    """

    jobs: List[JobResponse] = Field(default_factory=list)