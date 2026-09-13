from typing import Any

from app.services.tools.base import (
    BaseTool,
    ToolContext,
)

from app.services.rag.generator import (
    generate_rag_answer,
)


class RAGSearchTool(BaseTool):

    name = "company_knowledge_search"

    description = (
        "Search the Company's internal documents "
        "and answer questions using permission-aware "
        "retrieval augmented generation."
    )

    category = "knowledge"

    @property
    def input_schema(self) -> dict[str, Any]:

        return {
            "type": "object",
            "properties": {
                "question": {
                    "type": "string",
                    "description": (
                        "Question to search in "
                        "Company OS knowledge."
                    ),
                },
                "top_k": {
                    "type": "integer",
                    "description": (
                        "Number of document chunks "
                        "to retrieve."
                    ),
                    "minimum": 1,
                    "maximum": 20,
                },
                "document_id": {
                    "type": "integer",
                    "description": (
                        "Optional document ID filter."
                    ),
                },
            },
            "required": [
                "question",
            ],
        }

    def execute(
        self,
        context: ToolContext,
        arguments: dict[str, Any],
    ) -> Any:

        question = arguments.get(
            "question"
        )

        if not question:
            raise ValueError(
                "question is required."
            )

        if context.db is None:
            raise ValueError(
                "Database session is required "
                "for knowledge search."
            )

        if context.user_id is None:
            raise ValueError(
                "user_id is required "
                "for knowledge search."
            )

        if context.workspace_id is None:
            raise ValueError(
                "workspace_id is required "
                "for knowledge search."
            )

        top_k = arguments.get(
            "top_k",
            5,
        )

        document_id = arguments.get(
            "document_id"
        )

        result = generate_rag_answer(
            db=context.db,
            question=question,
            user_id=context.user_id,
            role=context.metadata.get(
                "role",
                "member",
            ),
            workspace_id=context.workspace_id,
            top_k=top_k,
            document_id=document_id,
        )

        return {
            "answer": result["answer"],
            "citations": result.get(
                "citations",
                [],
            ),
            "sources": result.get(
                "sources",
                [],
            ),
            "metrics": result.get(
                "metrics"
            ),
        }
