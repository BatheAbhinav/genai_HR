import logging
import time
from contextlib import contextmanager
from typing import Any

logger = logging.getLogger("policy_search")


@contextmanager
def log_duration(operation: str, **context: Any):
    """Context manager that logs start, completion, and elapsed time for any operation."""
    logger.info("Starting %s | %s", operation, _fmt(context))
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.error("Failed %s after %dms: %s | %s", operation, elapsed_ms, exc, _fmt(context))
        raise
    else:
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        logger.info("Completed %s in %dms | %s", operation, elapsed_ms, _fmt(context))


def log_query(user_id: str, question: str, confidence: float, escalated: bool, latency_ms: int) -> None:
    logger.info(
        "Query processed | user=%s | confidence=%.3f | escalated=%s | latency_ms=%d | question=%.80s",
        user_id,
        confidence,
        escalated,
        latency_ms,
        question,
    )


def log_ingestion(title: str, policy_type: str, chunk_count: int) -> None:
    logger.info(
        "Document ingested | title=%s | policy_type=%s | chunks=%d",
        title,
        policy_type,
        chunk_count,
    )


def _fmt(ctx: dict) -> str:
    return " | ".join(f"{k}={v}" for k, v in ctx.items())
