from fastapi import APIRouter, Depends, HTTPException
from schemas.jobs import JobResponse
from utils.logger_config import get_logger
from redisStore.queue import get_redis_con
from redis import Redis
from services import jobs

# API router for job-releated endpoints which defines the root path as /api/jobs
router = APIRouter(prefix="/api/jobs", tags=["jobs"]) 
logger = get_logger(__name__) # create logger instance with the name of current module

def get_redis():
    """
    Get Redis connection
    """
    return get_redis_con()

# GET /api/jobs/results/{job_id}
@router.get(
        "/results/{job_id}",
        response_model=JobResponse,
        summary="Polls job status by job ID",
        description="Checks the status of a job using its job ID from the Redis queue.",
        responses={
            200: {
                "description": "Job found, response contains status",
                "model": JobResponse,
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
async def get_job_results(job_id: str, redis: Redis = Depends(get_redis)):
    """
    Polls the status for a job using its job ID from Redis queue.

    Args:
        job_id (str): The unique identifier of the job.

    Returns:
        Response (JobResponse): A response containing the job's status including result or error in the form of the JobResponse schema.

    Raises:
        HTTPException: If job id is invalid, the job is not found or an error occurs while processing the job.
    """
    job_id = job_id.strip()
    logger.info(f"Fetching results for job_id: {job_id}")
    
    # Fetch the job from Redis using the provided job_id
    try:
        # verify that job isn't whitespace
        if not job_id:
            raise HTTPException(status_code=400, 
            detail="Job ID can't be empty or whitespace.")
        job_status_data = jobs.get_job_status(job_id, redis)
        
        # If job not found
        if job_status_data is None:
            logger.warning(f"Job not found: {job_id}")
            raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")
        logger.info(f"Job status retrieved successfully for job_id: {job_id}")
        return job_status_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"System error fetching job {job_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"System error fetching job {job_id}: {str(e)}")