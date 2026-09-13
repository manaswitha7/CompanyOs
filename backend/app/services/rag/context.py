from typing import Any


DEFAULT_MAX_CHARACTERS = 12000


def build_context(
    retrieved_chunks: list[dict[str, Any]],
    max_characters: int = DEFAULT_MAX_CHARACTERS,
) -> str:
    """
    Convert retrieved chunks into an LLM-ready context.

    Each source keeps its document and page metadata
    so the final answer can provide citations.

    max_characters acts as a hard limit on the
    generated context size.
    """

    if not retrieved_chunks:
        return ""

    if max_characters <= 0:
        raise ValueError(
            "max_characters must be greater than 0"
        )

    context_parts = []
    total_characters = 0

    for index, chunk in enumerate(
        retrieved_chunks,
        start=1,
    ):
        filename = (
            chunk.get("filename")
            or "Unknown document"
        )

        page_number = chunk.get(
            "page_number"
        )

        content = (
            chunk.get("content")
            or ""
        ).strip()

        if not content:
            continue

        if page_number is not None:
            source = (
                f"{filename}, "
                f"page {page_number}"
            )
        else:
            source = filename

        source_block = (
            f"SOURCE {index}\n"
            f"Document: {source}\n"
            f"Chunk: {chunk['chunk_id']}\n"
            f"Content:\n"
            f"{content}"
        )

        remaining = (
            max_characters
            - total_characters
        )

        if remaining <= 0:
            break

        # If the complete source fits,
        # add it normally.
        if len(source_block) <= remaining:
            context_parts.append(
                source_block
            )

            total_characters += len(
                source_block
            )

            continue

        # The source is larger than the
        # remaining context budget.
        truncation_marker = (
            "\n[Context truncated]"
        )

        available = (
            remaining
            - len(truncation_marker)
        )

        if available > 0:
            source_block = (
                source_block[:available]
                + truncation_marker
            )

            context_parts.append(
                source_block
            )

            total_characters += len(
                source_block
            )

        else:
            # There isn't enough room even
            # for the truncation marker.
            source_block = source_block[
                :remaining
            ]

            context_parts.append(
                source_block
            )

            total_characters += len(
                source_block
            )

        break

    return "\n\n".join(
        context_parts
    )
