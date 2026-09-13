import json
import os

import redis
from dotenv import load_dotenv


load_dotenv()


REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://localhost:6379/0",
)

INGESTION_QUEUE = "companyos:ingestion"


redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=None,
)


def enqueue_ingestion(
    document_id: int,
) -> None:
    """
    Add a document ingestion job to Redis.
    """

    job = {
        "document_id": document_id,
    }

    redis_client.rpush(
        INGESTION_QUEUE,
        json.dumps(job),
    )


def dequeue_ingestion():
    """
    Wait for and retrieve the next ingestion job.

    Uses a finite Redis blocking timeout so the
    worker can safely continue polling.
    """

    result = redis_client.blpop(
        INGESTION_QUEUE,
        timeout=5,
    )

    if result is None:
        return None

    _, job_data = result

    return json.loads(job_data)


def check_redis_connection() -> bool:
    """
    Check whether Redis is reachable.
    """

    return bool(
        redis_client.ping()
    )
