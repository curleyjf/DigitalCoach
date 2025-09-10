import sys
from rq import Worker
from redisStore.myconnection import get_redis_con
from utils.logger_config import get_logger

logger = get_logger(__name__)

# Default list of queues to listen for jobs on
DEFAULT_QUEUES = ["default", "high", "low"]


def get_worker(queues=None):
    """
    Create and return a worker instance
    
    Args:
        queues: List of queue names to listen on (default: ["default", "high", "low"])
    
    Returns:
        Worker: RQ Worker instance
    """
    if queues is None:
        queues = DEFAULT_QUEUES
    
    conn = get_redis_con()
    return Worker(queues, connection=conn)


if __name__ == "__main__":
    # Accept queue names as command-line arguments
    if len(sys.argv) > 1:
        queue_names = sys.argv[1:]
        logger.info(f"Starting worker listening to queues: {', '.join(queue_names)}")
        worker = get_worker(queue_names)
    else:
        logger.info(f"Starting worker listening to default queues: {', '.join(DEFAULT_QUEUES)}")
        worker = get_worker()
    
    worker.work(with_scheduler=True)
