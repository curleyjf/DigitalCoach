from fastapi import APIRouter, HTTPException, Depends
from schemas import JobId, AudioAnalysisRequest, AudioAnalysisResponse
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger
from redis import Redis
from services import jobs, orchestrator
from pydantic import ValidationError

logger = get_logger(__name__)

router = APIRouter(prefix="/api/audio_analysis", tags=["analysis"])       

def get_redis():
    """
    Returns a Redis connnection instance.
    """
    return get_redis_con()

# POST /api/audio_analysis
@router.post(
    "/",
    response_model=JobId,
    summary="Start an audio analysis job for the given video",
    description="Starts a background job to analyze audio using AssemblyAI",
)
async def start_audio_analysis_job(request: AudioAnalysisRequest) -> JobId:
    """
    Start a job to analyze audio from the video URL using AssemblyAI.

    This will extract audio and send it to AssemblyAI for:
    - Transcription
    - Sentiment analysis
    - Auto-highlights (key phrases)
    - Topic detection (IAB categories)

    Args:
        request: The AudioAnalysisRequest object that contains the video_url for analysis
    Returns:
        JobId: The job ID of the started job
    Raises:
        HTTPException: If the job cannot be started
    """
    try:
        # Use default video URL for testing if not provided
        # if not request.video_url:
        #     video_url = "https://assembly.ai/wildfires.mp3"
        
        # The actual video URL to analyze
        video_url = str(request.video_url)
        
        logger.info(f"Started audio analysis job for URL: {video_url}")
        
        # Queue the audio analysis job
        job_id = orchestrator.start_audio_analysis(video_url)
        
        logger.info(f"Successfully started audio analysis job: {job_id}")
        return JobId(job_id=job_id)
    # Catch validation errors from Pydantic
    except ValidationError as e:
        logger.error(f"Validation error starting audio analysis job: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error starting audio analysis job: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# GET /api/audio_analysis/{job_id}
@router.get(
    "/{job_id}",
    response_model=AudioAnalysisResponse,
    summary="Get the status of an audio analysis job",
    description="Check the status of a previously started audio analysis job",
    responses={
        200: {
            "description": "Job found, response contains status",
            "model": AudioAnalysisResponse,
        }, 
        400: {
            "description": "Job ID contains whitespace",
        },
        404: {
            "description": "Unable to find job",
        },
        500: {
            "description": "System error when trying to fetch status",
        },
    },
)
async def get_audio_analysis_job(job_id: str, redis: Redis = Depends(get_redis)) -> AudioAnalysisResponse:
    """
    Get the status of an audio analysis job.

    Args:
        job_id (str): The ID of the audio analysis job to get the status of
    Returns:
        Response (AudioAnalysisResponse): The job status in the form of the AudioAnalysisResponse schema
    Raises:
        HTTPException: If the job cannot be found or an error occurs
    """
    try:
        job_id = job_id.strip()
        # verify that job_id isn't whitespace
        if not job_id:
            raise HTTPException(status_code=400, detail="job_id cannot be whitespace")

        logger.info(f"Fetching audio analysis job status for job_id: {job_id}")        
        job_status_data = jobs.get_job_status(job_id, redis)
        
        # Handle if job doesn't exist
        if job_status_data is None:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

        # convert JobResponse to AudioAnalysisResponse
        return AudioAnalysisResponse(**job_status_data.model_dump())

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting audio analysis job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
