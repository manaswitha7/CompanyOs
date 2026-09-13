import logging
from typing import Any


logger = logging.getLogger("company_os.rag")


# Approximate cost per 1K tokens.
# Keep this configurable later when actual provider pricing is added.
MODEL_COST_PER_1K = {
    "default": 0.0,
}


def start_timer():
    import time
    return time.perf_counter()


def elapsed_ms(start_time: float) -> float:
    import time

    return round(
        (time.perf_counter() - start_time) * 1000,
        2,
    )


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str | None,
) -> float:
    """
    Estimate LLM request cost.

    Pricing is intentionally configurable.
    """

    rate = MODEL_COST_PER_1K.get(
        model or "default",
        MODEL_COST_PER_1K["default"],
    )

    total_tokens = (
        input_tokens + output_tokens
    )

    return round(
        (total_tokens / 1000) * rate,
        6,
    )


def log_rag_metrics(
    *,
    question: str,
    provider: str | None,
    model: str | None,
    retrieval_latency_ms: float,
    llm_latency_ms: float,
    total_latency_ms: float,
    retrieved_chunks: int,
    citation_count: int,
    success: bool,
    input_tokens: int = 0,
    output_tokens: int = 0,
    error: str | None = None,
) -> dict[str, Any]:

    total_tokens = (
        input_tokens + output_tokens
    )

    estimated_cost = estimate_cost(
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        model=model,
    )

    metrics = {
        "question_length": len(question),

        "provider": provider,
        "model": model,

        "retrieval_latency_ms":
            retrieval_latency_ms,

        "llm_latency_ms":
            llm_latency_ms,

        "total_latency_ms":
            total_latency_ms,

        "retrieved_chunks":
            retrieved_chunks,

        "citation_count":
            citation_count,

        "input_tokens":
            input_tokens,

        "output_tokens":
            output_tokens,

        "total_tokens":
            total_tokens,

        "estimated_cost":
            estimated_cost,

        "success":
            success,

        "error":
            error,
    }

    logger.info(
        "RAG_METRICS %s",
        metrics,
    )

    return metrics
