import os
from redis import Redis, from_url
from utils.logger_config import get_logger

logger = get_logger(__name__)


def get_redis_con() -> Redis:
    """
    Create a secure Redis connection with authentication.

    Returns:
        Redis: Authenticated Redis connection
    """
    try:
        # Check if a redis_url environment variable is available first
        redis_url = os.getenv("REDIS_URL")
        if redis_url:
            return from_url(redis_url, decode_responses=False)
        # Otherwise use individual connection parameters
        redis_conn = Redis(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            password=os.getenv("REDIS_PASSWORD"),
            decode_responses=False,
            socket_timeout=5,
            socket_connect_timeout=5,
            socket_keepalive=True,
            health_check_interval=30,
        )
        # Test the connection
        return redis_conn
    except Exception as e:
        logger.error(f"Redis connection error: {str(e)}")
        raise e
