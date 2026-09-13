from typing import Any

from app.services.rag.generator import generate_rag_answer


# ============================================================
# ANSWER MATCHING
# ============================================================

def answer_matches(
    answer: str,
    case: dict[str, Any],
) -> bool:
    """
    Check whether the generated answer contains
    the required answer keywords.

    If answer_keywords are configured, all keywords
    must appear in the generated answer.

    If no keywords are configured, fall back to
    expected_answer substring matching.
    """

    normalized_answer = (
        answer or ""
    ).strip().lower()

    keywords = [
        str(keyword).strip().lower()
        for keyword in case.get(
            "answer_keywords",
            [],
        )
        if str(keyword).strip()
    ]

    expected_answer = (
        case.get("expected_answer") or ""
    ).strip().lower()

    # Nothing configured
    if not keywords and not expected_answer:
        return False

    # Preferred evaluation method:
    # semantic content represented by required keywords
    if keywords:
        return all(
            keyword in normalized_answer
            for keyword in keywords
        )

    # Fallback
    return expected_answer in normalized_answer


# ============================================================
# CITATION MATCHING
# ============================================================

def citation_matches(
    citations: list[dict[str, Any]],
    case: dict[str, Any],
) -> bool:
    """
    Check whether at least one citation matches
    the expected document and page.
    """

    expected_document = (
        case.get("expected_document") or ""
    ).strip()

    expected_page = case.get(
        "expected_page"
    )

    # No citation expectation configured.
    if not expected_document and expected_page is None:
        return False

    for citation in citations:

        document_match = (
            not expected_document
            or citation.get("filename")
            == expected_document
        )

        page_match = (
            expected_page is None
            or citation.get("page_number")
            == expected_page
        )

        if document_match and page_match:
            return True

    return False


# ============================================================
# EVALUATE ONE CASE
# ============================================================

def evaluate_case(
    db,
    case: dict[str, Any],
    workspace_id: int,
) -> dict[str, Any]:
    """
    Run one golden Q&A case through the real RAG pipeline.
    """

    result = generate_rag_answer(
        db=db,
        question=case["question"],
        workspace_id=workspace_id,
        top_k=5,
    )

    answer = result.get(
        "answer",
        "",
    )

    citations = result.get(
        "citations",
        [],
    )

    answer_match = answer_matches(
        answer=answer,
        case=case,
    )

    citation_match = citation_matches(
        citations=citations,
        case=case,
    )

    # A case passes only when both configured
    # answer and citation expectations match.
    expected_answer_configured = bool(
        case.get("expected_answer")
        or case.get("answer_keywords")
    )

    expected_citation_configured = bool(
        case.get("expected_document")
        or case.get("expected_page") is not None
    )

    checks = []

    if expected_answer_configured:
        checks.append(answer_match)

    if expected_citation_configured:
        checks.append(citation_match)

    passed = (
        all(checks)
        if checks
        else False
    )

    return {
        "id": case["id"],
        "question": case["question"],
        "answer": answer,
        "citations": citations,
        "answer_match": answer_match,
        "citation_match": citation_match,
        "passed": passed,
        "metrics": result.get(
            "metrics",
            {},
        ),
    }


# ============================================================
# EVALUATE DATASET
# ============================================================

def evaluate_dataset(
    db,
    dataset: list[dict[str, Any]],
    workspace_id: int,
) -> dict[str, Any]:
    """
    Evaluate the complete golden dataset
    against the real Company OS RAG pipeline.
    """

    results = []

    for case in dataset:

        result = evaluate_case(
            db=db,
            case=case,
            workspace_id=workspace_id,
        )

        results.append(result)

    total = len(results)

    passed = sum(
        1
        for result in results
        if result["passed"]
    )

    answer_matches = sum(
        1
        for result in results
        if result["answer_match"]
    )

    citation_matches = sum(
        1
        for result in results
        if result["citation_match"]
    )

    evaluation_accuracy = (
        passed / total
        if total
        else 0.0
    )

    answer_accuracy = (
        answer_matches / total
        if total
        else 0.0
    )

    citation_accuracy = (
        citation_matches / total
        if total
        else 0.0
    )

    return {
        "total_cases": total,
        "passed_cases": passed,
        "failed_cases": total - passed,
        "evaluation_accuracy": evaluation_accuracy,
        "answer_matches": answer_matches,
        "answer_accuracy": answer_accuracy,
        "citation_matches": citation_matches,
        "citation_accuracy": citation_accuracy,
        "results": results,
    }
