from fastapi import APIRouter
from rq.job import Job
import json
from utils.logger_config import get_logger
from redisStore.queue import get_redis_con

logger = get_logger(__name__)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.get("/results/{job_id}")
async def get_job_results(job_id: str):
    """
    GET route that returns the results of a job.

    This endpoint fetches the results of a job from the Redis queue using the job ID.
    It checks the status of the job and returns the result if the job is finished.
    If the job is not found or not finished, it returns an appropriate message.

    Args:
        job_id (str): The unique identifier of the job.

    Returns:
        Response: A JSON response containing the job result if finished, or a message indicating the job status.
    """
    logger.info(f"Fetching results for job_id: {job_id}")
    # get connection
    conn = get_redis_con()
    try:
        job = Job.fetch(job_id, connection=conn)
    except Exception as e:
        logger.warning(f"Job not found: {job_id}. Error: {str(e)}")
        return ({"message": "Job not found.", "status": "error"}), 404
    if not job.is_finished:
        logger.info(f"Job is not finished yet: {job_id}")
        return {"message": "Job is not finished yet.", "status": "pending"}
    try:
        result = job.result
        if "errors" in result:
            return ({"errors": result["errors"]}), 400
        json_string = json.dumps(result)
        logger.info(f"Job finished successfully: {job_id}")
        return {"result": json.loads(json_string), "status": "success"}
    except Exception as e:
        logger.error(f"Error processing job result for job_id {job_id}: {str(e)}")
        return (
            (
                {
                    "message": "Error processing job result",
                    "error": str(e),
                    "status": "error",
                }
            ),
            500,
        )
