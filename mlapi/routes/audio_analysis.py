from fastapi import APIRouter, HTTPException
from schemas.jobs import JobId, JobResponse
from schemas.create_answer import AudioSentimentResult, AudioAnalysisJob
from redisStore.queue import add_task_to_queue
from tasks.assemblyai_api import detect_audio_sentiment
from rq.job import Job
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger
from pydantic import BaseModel

logger = get_logger(__name__)

router = APIRouter(prefix="/api/audio_analysis", tags=["analysis"])


class AudioAnalysisRequest(BaseModel):
    """
    Request to start an audio analysis job
    """

    video_url: str


@router.post(
    "/",
    response_model=JobId,
    summary="Start an audio analysis job for the given video",
    description="Starts a background job to analyze audio using AssemblyAI",
)
async def start_audio_analysis_job(request: AudioAnalysisRequest):
    """
    Start a job to analyze audio from the video URL using AssemblyAI.

    This will extract audio and send it to AssemblyAI for:
    - Transcription
    - Sentiment analysis
    - Auto-highlights (key phrases)
    - Topic detection (IAB categories)
    """
    try:
        # Use default video URL for testing if not provided
        video_url = request.video_url or "https://assembly.ai/wildfires.mp3"

        # Start the audio analysis job
        job = add_task_to_queue(detect_audio_sentiment, video_url)

        logger.info(f"Started audio analysis job: {job.get_id()}")
        return {"job_id": job.get_id()}
    except Exception as e:
        logger.error(f"Error starting audio analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/{job_id}",
    response_model=JobResponse,
    summary="Get the status of an audio analysis job",
    description="Check the status of a previously started audio analysis job",
)
async def get_audio_analysis_job(job_id: str):
    """
    Get the status of an audio analysis job.

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
        logger.error(f"Error getting audio analysis job {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")


@router.get(
    "/{job_id}/result",
    response_model=AudioSentimentResult,
    summary="Get the result of a completed audio analysis job",
    description="Get the full result of a completed audio analysis job",
)
async def get_audio_analysis_result(job_id: str):
    """
    Get the result of a completed audio analysis job.

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
        logger.error(f"Error getting audio analysis result {job_id}: {str(e)}")
        raise HTTPException(status_code=404, detail=f"Job not found: {str(e)}")
