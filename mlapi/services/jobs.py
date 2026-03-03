from rq.job import Job
from rq.exceptions import NoSuchJobError
from redis import Redis
from schemas import JobResponse, JobStatus
from utils.logger_config import get_logger

logger = get_logger(__name__) 

def get_job_status(job_id: str, redis_conn: Redis) -> JobResponse:
    """
    Get the status of a job with the given job ID in the format of the JobResponse schema.
    
    Args:
        job_id (str): ID of the job to check
        redis_conn (Redis): Redis connection object
    Returns:
        Response (JobResponse): A dictionary containing the job status and result or error information in the format of the JobResponse schema.
    """ 

    # Attempt to get job object with given job ID
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except NoSuchJobError:
        return None
    
    # Initialize job status response based on JobResponse schema
    response = JobResponse(
        job_id = job_id,
        status=JobStatus.PENDING, # assume job is still in the queue
        result=None, 
        error=None)    

    # check job status
    # job failed, return failed status and error information
    if job.is_failed:
        logger.error(f"Job {job_id} failed with error: {str(job.exc_info)}")
        response.status = JobStatus.FAILED
        response.error = str(job.exc_info)
        return response
    # job finished, return complete status and result
    elif job.is_finished:
        # check if job finished with exception
        if isinstance(job.result, Exception):
            logger.error(f"Job {job_id} completed with an excewption: {str(job.result)}")
            response.status = JobStatus.FAILED
            response.error = str(job.result)
            return response

        logger.info(f"Job {job_id} completed successfully.")
        response.status = JobStatus.COMPLETED
        response.result = job.result
        return response
        
    # job still processing, return processing status
    elif job.is_started:
        logger.info(f"Job {job_id} is still processing.")
        response.status = JobStatus.PROCESSING
        return response
    
    # job is still pending in the queue
    logger.info(f"Job {job_id} is still pending in the queue.")
    return response
