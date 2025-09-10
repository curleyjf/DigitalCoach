import time
from typing import Never, Set, Iterator
from utils.logger_config import get_logger
from redisStore.myconnection import get_redis_con
from rq import Queue

logger = get_logger(__name__)

ALL_JOBS: Set[str] = set()
RESULT_ENCODING = "result".encode("utf-8")
FINISHED_ENCODING = "finished".encode("utf-8")


def _update_all_jobs(redis_conn) -> Iterator[str]:
    """
    Get finished jobs from Redis.

    Args:
        redis_conn: Redis connection

    Yields:
        str: Job ID for each finished job
    """
    try:
        keys = redis_conn.keys("rq:job:*")
        for key in keys:
            key_str = key.decode("utf-8")
            status = redis_conn.hgetall(key)
            status = {k.decode("utf-8"): v for k, v in status.items()}
            if status.get("status") == FINISHED_ENCODING:
                yield key_str
    except Exception as e:
        logger.error(f"Error updating jobs: {str(e)}")


def get_queue_stats(redis_conn) -> dict:
    """
    Get statistics about all queues

    Args:
        redis_conn: Redis connection

    Returns:
        dict: Statistics about each queue
    """
    try:
        queues = ["default", "high", "low"]
        stats = {}

        for queue_name in queues:
            q = Queue(queue_name, connection=redis_conn)
            stats[queue_name] = {
                "count": q.count,
                "failed": q.failed_job_registry.count,
                "started": q.started_job_registry.count,
                "deferred": q.deferred_job_registry.count,
                "scheduled": q.scheduled_job_registry.count,
            }

        return stats
    except Exception as e:
        logger.error(f"Error getting queue stats: {str(e)}")
        return {}


def poll_connection(redis_connection) -> Never:
    """
    Continuously poll the Redis connection for jobs.

    Args:
        redis_connection: Redis connection
    """
    while True:
        try:
            # Log finished jobs
            finished_jobs = list(_update_all_jobs(redis_connection))
            if finished_jobs:
                logger.info(f"Finished jobs: {len(finished_jobs)} {finished_jobs}")

            # Log queue stats every 10 seconds
            stats = get_queue_stats(redis_connection)
            logger.info(f"Queue stats: {stats}")

            time.sleep(10)
        except Exception as e:
            logger.error(f"Error in poll_connection: {str(e)}")
            time.sleep(10)


def run_monitor():
    """Run the job monitor"""
    redis_conn = get_redis_con()
    logger.info("Starting job monitor")
    poll_connection(redis_conn)


if __name__ == "__main__":
    run_monitor()
