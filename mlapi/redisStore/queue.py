from typing import Callable
from rq.job import Job
from rq.queue import Queue
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger

logger = get_logger(__name__)


def get_queue(queue_name="default") -> Queue:
    """
    Get a Queue instance with the specified name.

    Args:
        queue_name (str): Name of the queue

    Returns:
        Queue: RQ Queue instance
    """
    conn = get_redis_con()
    return Queue(name=queue_name, connection=conn)


def add_task_to_queue(
    task: Callable,
    *args,
    depends_on=None,
) -> Job:
    """
    Add a task to the Redis queue with proper error handling.

    Args:
        task: The task function to be executed
        args: List of arguments to pass to the task

    Returns:
        Job: The enqueued job
    """
    try:
        queue = get_queue("default")
        # Set default empty list if args is None
        if args is None:
            args = []

        job = queue.enqueue(
            task,
            *args,
            depends_on=depends_on,
        )
        logger.info(f"Task {task.__name__} enqueued with job ID: {job.id}")
        return job
    except Exception as e:
        logger.error(f"Failed to enqueue task: {str(e)}")
        raise e
