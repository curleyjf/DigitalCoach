from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from schemas.jobs import JobId, JobResponse, CreateAnswerJobRequest
from schemas.create_answer import CreateAnswer
from redisStore.queue import add_task_to_queue
from tasks.create_answer_task import (
    create_answer,
    start_audio_analysis_job,
    start_facial_analysis_job,
)
from rq.job import Job
from redisStore.myconnection import get_redis_con
from typing import Optional
from utils.logger_config import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/create_answer", tags=["analysis"])


@router.post(
    "/",
    response_model=JobId,
    summary="Start an answer generation job for the given video",
    description="Starts a background job to analyze a video and generate an answer",
)
async def create_answer_job(request: CreateAnswerJobRequest):
    """
    Start a job to generate an answer for the video URL.

    This will:
    1. Start an audio analysis job using AssemblyAI
    2. Start a facial analysis job using DeepFace
    3. Start a create_answer job that depends on the first two jobs
    """
    try:
        # Use default video URL for testing if not provided
        video_url = request.video_url or "https://assembly.ai/wildfires.mp3"

        # Start the audio and facial analysis jobs
        audio_job_id = start_audio_analysis_job(video_url)
        facial_job_id = start_facial_analysis_job(video_url)

        # Start the create_answer job that depends on the first two jobs
        job = add_task_to_queue(create_answer, video_url, audio_job_id, facial_job_id)

        logger.info(f"Started create_answer job: {job.get_id()}")
        return {"job_id": job.get_id()}
    except Exception as e:
        logger.error(f"Error starting create_answer job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get the status of a create_answer job",
    description="Check the status of a previously started create_answer job",
)
async def get_create_answer_job(job_id: str):
    """
    Get the status of a create_answer job.

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
                "result": result.dict() if hasattr(result, "dict") else result,
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
        logger.error(f"Error getting create_answer job {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@router.get(
    "/{job_id}/result",
    response_model=CreateAnswer,
    summary="Get the result of a completed create_answer job",
    description="Get the full result of a completed create_answer job",
)
async def get_create_answer_result(job_id: str):
    """
    Get the result of a completed create_answer job.

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
        logger.error(f"Error getting create_answer result {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
