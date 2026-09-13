from app.services.llm.provider import LLMProvider
from app.services.rag.context import build_context
from app.services.rag.retriever import retrieve_chunks
from app.services.observability.rag_metrics import (
    elapsed_ms,
    log_rag_metrics,
    start_timer,
)


llm_provider = LLMProvider()


def generate_rag_answer(
    db,
    question: str,
    user_id: int,
    role: str,
    workspace_id: int,
    top_k: int = 5,
    document_id: int | None = None,
    conversation_context: str = "",
):
    """
    Generate an answer using retrieved company documents.

    Permission-aware RAG pipeline:

        question
            ↓
        authenticated user
            ↓
        document permission check
            ↓
        permission-filtered hybrid retrieval
            ↓
        context building
            ↓
        conversation context
            ↓
        LLM
            ↓
        answer + citations + metrics
    """

    # --------------------------------------------------
    # 1. Validate question
    # --------------------------------------------------

    if not question or not question.strip():
        raise ValueError(
            "Question cannot be empty."
        )

    question = question.strip()

    # --------------------------------------------------
    # 2. Start total timer
    # --------------------------------------------------

    total_start = start_timer()

    # --------------------------------------------------
    # 3. Permission-aware retrieval
    # --------------------------------------------------

    retrieval_start = start_timer()

    try:

        retrieved_chunks = retrieve_chunks(
            db=db,
            query=question,
            user_id=user_id,
            role=role,
            workspace_id=workspace_id,
            top_k=top_k,
            document_id=document_id,
        )

        retrieval_latency_ms = elapsed_ms(
            retrieval_start
        )

    except Exception as exc:

        retrieval_latency_ms = elapsed_ms(
            retrieval_start
        )

        total_latency_ms = elapsed_ms(
            total_start
        )

        log_rag_metrics(
            question=question,
            provider=llm_provider.provider,
            model=llm_provider.model,
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=0.0,
            total_latency_ms=total_latency_ms,
            retrieved_chunks=0,
            citation_count=0,
            success=False,
            error=str(exc),
        )

        raise

    # --------------------------------------------------
    # 4. No accessible/relevant results
    # --------------------------------------------------

    if not retrieved_chunks:

        total_latency_ms = elapsed_ms(
            total_start
        )

        metrics = log_rag_metrics(
            question=question,
            provider=llm_provider.provider,
            model=llm_provider.model,
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=0.0,
            total_latency_ms=total_latency_ms,
            retrieved_chunks=0,
            citation_count=0,
            success=True,
            error=None,
        )

        return {
            "answer": (
                "I couldn't find relevant information "
                "in the available company documents."
            ),
            "citations": [],
            "sources": [],
            "metrics": metrics,
        }

    # --------------------------------------------------
    # 5. Build bounded document context
    # --------------------------------------------------

    context = build_context(
        retrieved_chunks,
        max_characters=12000,
    )

    # --------------------------------------------------
    # 6. Build conversation context
    # --------------------------------------------------

    conversation_section = ""

    if conversation_context.strip():

        conversation_section = f"""
PREVIOUS CONVERSATION:

{conversation_context}

Use the previous conversation only to understand
references and context in the user's current question.

Do NOT treat previous conversation as authoritative
company knowledge.

Company knowledge must come from the retrieved
document CONTEXT below.
"""

    # --------------------------------------------------
    # 7. Build grounded RAG prompt
    # --------------------------------------------------

    prompt = f"""
You are the Company OS knowledge assistant.

Your job is to answer the user's question using
ONLY the retrieved company knowledge provided below.

{conversation_section}

Rules:

1. Do not invent facts.

2. Do not use outside knowledge.

3. If the retrieved context does not contain enough
   information to answer the question, clearly say:

   "The available company documents do not contain
   enough information to answer this."

4. Keep the answer concise and factual.

5. Previous conversation may be used only to
   understand references such as:
   - "it"
   - "that"
   - "they"
   - "the previous policy"
   - "what about eligibility?"

6. Do not use previous conversation as a source
   of company facts.

7. Company facts must come from the retrieved
   document context.

8. Cite the source document and page number whenever
   the information comes from a PDF.

9. Use this citation format:

   [Document Name, p. X]

10. Do not create citations for information that
    is not present in the retrieved context.

QUESTION:

{question}

RETRIEVED COMPANY KNOWLEDGE:

{context}
"""

    # --------------------------------------------------
    # 8. Generate answer
    # --------------------------------------------------

    llm_start = start_timer()

    try:

        answer = llm_provider.generate(
            prompt=prompt,
            temperature=0.2,
        )

        llm_latency_ms = elapsed_ms(
            llm_start
        )

    except Exception as exc:

        llm_latency_ms = elapsed_ms(
            llm_start
        )

        total_latency_ms = elapsed_ms(
            total_start
        )

        log_rag_metrics(
            question=question,
            provider=llm_provider.provider,
            model=llm_provider.model,
            retrieval_latency_ms=retrieval_latency_ms,
            llm_latency_ms=llm_latency_ms,
            total_latency_ms=total_latency_ms,
            retrieved_chunks=len(
                retrieved_chunks
            ),
            citation_count=0,
            success=False,
            error=str(exc),
        )

        raise

    # --------------------------------------------------
    # 9. Build structured citations
    # --------------------------------------------------

    citations = []

    seen = set()

    for chunk in retrieved_chunks:

        filename = chunk.get(
            "filename"
        )

        page_number = chunk.get(
            "page_number"
        )

        citation_key = (
            filename,
            page_number,
        )

        if citation_key in seen:
            continue

        seen.add(citation_key)

        citations.append(
            {
                "filename": filename,
                "page_number": page_number,
                "chunk_id": chunk[
                    "chunk_id"
                ],
            }
        )

    # --------------------------------------------------
    # 10. Calculate total latency
    # --------------------------------------------------

    total_latency_ms = elapsed_ms(
        total_start
    )

    # --------------------------------------------------
    # 11. Record metrics
    # --------------------------------------------------

    metrics = log_rag_metrics(
        question=question,
        provider=llm_provider.provider,
        model=llm_provider.model,
        retrieval_latency_ms=retrieval_latency_ms,
        llm_latency_ms=llm_latency_ms,
        total_latency_ms=total_latency_ms,
        retrieved_chunks=len(
            retrieved_chunks
        ),
        citation_count=len(
            citations
        ),
        success=True,
        error=None,
    )

    # --------------------------------------------------
    # 12. Return result
    # --------------------------------------------------

    return {
        "answer": answer,
        "citations": citations,
        "sources": retrieved_chunks,
        "metrics": metrics,
    }
