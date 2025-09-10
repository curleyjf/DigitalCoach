from fastapi import APIRouter, HTTPException
from schemas.jobs import JobId, JobResponse
from schemas.create_answer import EmotionDetectionResult, FacialAnalysisJob
from redisStore.queue import add_task_to_queue
from tasks.detect_emotions import detect_emotions
from rq.job import Job
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger
from pydantic import BaseModel, Field

logger = get_logger(__name__)

router = APIRouter(prefix="/api/facial_analysis", tags=["analysis"])


class FacialAnalysisRequest(BaseModel):
    """
    Request to start a facial analysis job
    """

    video_url: str
    sample_rate: int = Field(default=30, description="Process every Nth frame")


@router.post(
    "/",
    response_model=JobId,
    summary="Start a facial emotion analysis job for the given video",
    description="Starts a background job to analyze facial emotions using DeepFace",
)
async def start_facial_analysis_job(request: FacialAnalysisRequest):
    """
    Start a job to analyze facial emotions from the video URL using DeepFace.

    This will:
    - Extract frames from the video
    - Detect faces in each frame
    - Analyze emotions in detected faces
    - Aggregate results across all frames
    """
    try:
        # Use default video URL for testing if not provided
        video_url = request.video_url or "https://assembly.ai/wildfires.mp3"

        # Start the facial analysis job with the specified sample rate
        job = add_task_to_queue(detect_emotions, video_url, request.sample_rate)

        logger.info(f"Started facial analysis job: {job.get_id()}")
        return {"job_id": job.get_id()}
    except Exception as e:
        logger.error(f"Error starting facial analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get the status of a facial analysis job",
    description="Check the status of a previously started facial analysis job",
)
async def get_facial_analysis_job(job_id: str):
    """
    Get the status of a facial analysis job.

    Returns the job status and result if available.
    """
    try:
        job = Job.fetch(job_id, connection=get_redis_con())

        if job.is_finished:
            result = job.result
            if isinstance(result, Exception):
                return {
                    "job_id": job_id,
                    "status": "failed",
                    "error": str(result),
                }
            return {
                "job_id": job_id,
                "status": "completed",
                "result": result.model_dump()
                if hasattr(result, "model_dump")
                else result,
            }
        elif job.is_failed:
            return {
                "job_id": job_id,
                "status": "failed",
                "error": str(job.exc_info),
            }
        elif job.is_started:
            return {
                "job_id": job_id,
                "status": "processing",
            }
        else:
            return {
                "job_id": job_id,
                "status": "pending",
            }
    except Exception as e:
        logger.error(f"Error getting facial analysis job {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@router.get(
    "/{job_id}/result",
    response_model=EmotionDetectionResult,
    summary="Get the result of a completed facial analysis job",
    description="Get the full result of a completed facial analysis job",
)
async def get_facial_analysis_result(job_id: str):
    """
    Get the result of a completed facial analysis job.

    Only returns the result if the job is completed, otherwise raises an error.
    """
    try:
        job = Job.fetch(job_id, connection=get_redis_con())

        if job.is_finished:
            result = job.result
            if isinstance(result, Exception):
                raise HTTPException(status_code=500, detail=str(result))
            return result
        elif job.is_failed:
            raise HTTPException(status_code=500, detail=str(job.exc_info))
        else:
            raise HTTPException(status_code=202, detail="Job is still processing")
    except Exception as e:
        logger.error(f"Error getting facial analysis result {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
