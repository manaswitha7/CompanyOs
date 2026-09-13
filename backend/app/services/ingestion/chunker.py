def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[str]:
    """
    Split text into overlapping chunks.

    chunk_size:
        Maximum approximate number of characters per chunk.

    chunk_overlap:
        Number of characters shared between consecutive chunks.
    """

    if not text or not text.strip():
        return []

    text = text.strip()

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    start = 0
    text_length = len(text)

    while start < text_length:

        end = min(
            start + chunk_size,
            text_length,
        )

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= text_length:
            break

        start = end - chunk_overlap

    return chunks


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 1000,
    chunk_overlap: int = 150,
) -> list[dict]:
    """
    Split page-aware PDF text into overlapping chunks
    while preserving the page number.

    Input:
        [
            {
                "page_number": 1,
                "text": "..."
            },
            {
                "page_number": 2,
                "text": "..."
            }
        ]

    Output:
        [
            {
                "chunk_index": 0,
                "page_number": 1,
                "content": "..."
            },
            {
                "chunk_index": 1,
                "page_number": 2,
                "content": "..."
            }
        ]
    """

    if not pages:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []

    chunk_index = 0

    for page in pages:

        page_number = page["page_number"]
        text = page["text"]

        if not text or not text.strip():
            continue

        text = text.strip()

        start = 0
        text_length = len(text)

        while start < text_length:

            end = min(
                start + chunk_size,
                text_length,
            )

            content = text[start:end].strip()

            if content:

                chunks.append(
                    {
                        "chunk_index": chunk_index,
                        "page_number": page_number,
                        "content": content,
                    }
                )

                chunk_index += 1

            if end >= text_length:
                break

            start = end - chunk_overlap

    return chunks
