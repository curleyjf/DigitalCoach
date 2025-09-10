from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from rq.job import Job
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger
from tasks.starscores import predict_star_scores
from redisStore.queue import add_task_to_queue
import json

logger = get_logger(__name__)

router = APIRouter(prefix="/api/star_feedback", tags=["star_feedback"])


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


class StarFeedbackResponse(BaseModel):
    """
    Response model for STAR feedback
    """

    fulfilled_star: bool
    percentages: StarPercentages
    classifications: List[StarClassification]
    feedback: List[str]


@router.post("/analyze", response_model=dict)
async def analyze_star_method(request: StarFeedbackRequest):
    """
    Analyze text using the STAR method (Situation, Task, Action, Result)

    The STAR method is a structured way to respond to behavioral interview questions,
    which helps candidates provide concrete examples of their skills and experiences.

    This endpoint analyzes text to determine how well it follows the STAR structure
    and provides feedback on improving the response.

    Returns a job ID that can be used to track the status of the analysis.
    The results will be processed by success or failure handlers.
    """
    try:
        if not request.text or len(request.text.strip()) < 10:
            raise HTTPException(
                status_code=400,
                detail="Text is too short for analysis. Please provide a more detailed response.",
            )
        data = {"text": request.text}

        # Enqueue task with success and failure handlers
        job = add_task_to_queue(predict_star_scores, data)

        return {"job_id": job.id, "status": "queued"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing STAR method: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze text using STAR method: {str(e)}",
        )


@router.get("/result/{job_id}", response_model=dict)
async def get_star_feedback_result(job_id: str):
    """
    Get the result of a completed STAR feedback analysis job.

    Only returns the result if the job is completed, otherwise raises an error.
    """
    logger.info(f"Fetching results for job_id: {job_id}")
    # get connection
    conn = get_redis_con()
    try:
        job = Job.fetch(job_id, connection=conn)
    except Exception as e:
        logger.warning(f"Job not found: {job_id}. Error: {str(e)}")
        return HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
    if not job.is_finished:
        logger.info(f"Job is not finished yet: {job_id}")
        return HTTPException(status_code=202, detail="Job is still processing")
    try:
        result = job.result
        if "errors" in result:
            return HTTPException(status_code=400, detail=result["errors"])
        json_string = json.dumps(result)
        logger.info(f"Job finished successfully: {job_id}")
        return {"result": json.loads(json_string), "status": "success"}
    except Exception as e:
        logger.error(f"Error processing job result for job_id {job_id}: {str(e)}")
        return HTTPException(
            status_code=500, detail=f"Error processing job result: {str(e)}"
        )
