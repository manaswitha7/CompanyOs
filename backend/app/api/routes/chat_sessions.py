from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.models.user import User
from app.models.chat_session import ChatSession
from app.models.chat_message import ChatMessage
from app.services.auth.dependencies import get_current_user
from app.services.rag.generator import generate_rag_answer
from app.services.chat.router import (
    detect_tool,
    execute_chat_tool,
    build_tool_arguments,
)
from app.services.tools.setup import register_tools


router = APIRouter(
    prefix="/chat/sessions",
    tags=["Chat Sessions"],
)


# ==================================================
# REGISTER COMPANY OS TOOLS
# ==================================================

register_tools()


# ==================================================
# SCHEMAS
# ==================================================

class CreateSessionRequest(BaseModel):
    title: str = "New Conversation"


class SendMessageRequest(BaseModel):
    content: str = Field(
        ...,
        min_length=1,
        description="Message to send to Company OS",
    )


# ==================================================
# CREATE SESSION
# ==================================================

@router.post("")
def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    session = ChatSession(
        workspace_id=current_user.workspace_id,
        user_id=current_user.id,
        title=request.title.strip()
        or "New Conversation",
    )

    db.add(session)
    db.commit()
    db.refresh(session)

    return {
        "id": session.id,
        "title": session.title,
        "workspace_id": session.workspace_id,
        "user_id": session.user_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
    }


# ==================================================
# LIST SESSIONS
# ==================================================

@router.get("")
def list_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.workspace_id is None:
        raise HTTPException(
            status_code=400,
            detail="User is not assigned to a workspace.",
        )

    sessions = (
        db.query(ChatSession)
        .filter(
            ChatSession.workspace_id
            == current_user.workspace_id,
            ChatSession.user_id
            == current_user.id,
        )
        .order_by(
            ChatSession.updated_at.desc()
        )
        .all()
    )

    return {
        "sessions": [
            {
                "id": session.id,
                "title": session.title,
                "created_at": session.created_at,
                "updated_at": session.updated_at,
            }
            for session in sessions
        ]
    }


# ==================================================
# GET SESSION + MESSAGES
# ==================================================

@router.get("/{session_id}")
def get_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.workspace_id
            == current_user.workspace_id,
            ChatSession.user_id
            == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id
            == session.id
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )

    return {
        "id": session.id,
        "title": session.title,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "messages": [
            {
                "id": message.id,
                "role": message.role,
                "content": message.content,
                "created_at": message.created_at,
            }
            for message in messages
        ],
    }


# ==================================================
# SEND MESSAGE + TOOL / RAG
# ==================================================

@router.post("/{session_id}/messages")
def send_message(
    session_id: int,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # --------------------------------------------------
    # 1. Validate session ownership
    # --------------------------------------------------

    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.workspace_id
            == current_user.workspace_id,
            ChatSession.user_id
            == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    question = request.content.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    # --------------------------------------------------
    # 2. Save user message
    # --------------------------------------------------

    user_message = ChatMessage(
        session_id=session.id,
        role="user",
        content=question,
    )

    db.add(user_message)
    db.commit()
    db.refresh(user_message)

    # --------------------------------------------------
    # 3. Get previous conversation
    # --------------------------------------------------

    previous_messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.session_id
            == session.id,
            ChatMessage.id
            != user_message.id,
        )
        .order_by(
            ChatMessage.created_at.asc()
        )
        .all()
    )

    # --------------------------------------------------
    # 4. Build conversation context
    # --------------------------------------------------

    conversation_parts = []

    for message in previous_messages[-10:]:
        conversation_parts.append(
            f"{message.role.upper()}: "
            f"{message.content}"
        )

    conversation_context = "\n".join(
        conversation_parts
    )

    # --------------------------------------------------
    # 5. Detect Company OS tool
    # --------------------------------------------------

    tool_name = detect_tool(question)

    # --------------------------------------------------
    # 6. Execute tool OR use RAG
    # --------------------------------------------------

    if tool_name:

        try:
            # ------------------------------------------
            # Build tool arguments
            # ------------------------------------------

            arguments = build_tool_arguments(
                tool_name=tool_name,
                question=question
            )

            if tool_name == "create_task":

                arguments = {
                    "title": question,
                }

            # ------------------------------------------
            # Execute registered tool
            # ------------------------------------------

            tool_result = execute_chat_tool(
                tool_name=tool_name,
                arguments=arguments,
                user_id=current_user.id,
                workspace_id=current_user.workspace_id,
            )

            # ------------------------------------------
            # Convert tool result into chat response
            # ------------------------------------------

            answer = str(tool_result)

            citations = []

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Tool execution failed: {exc}",
            )

    else:

        # ----------------------------------------------
        # No tool detected → normal RAG
        # ----------------------------------------------

        try:

            result = generate_rag_answer(
                db=db,
                question=question,
                top_k=5,
                workspace_id=current_user.workspace_id,
                conversation_context=conversation_context,
            )

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"RAG generation failed: {exc}",
            )

        answer = result["answer"]

        citations = result["citations"]

    # --------------------------------------------------
    # 7. Save assistant message
    # --------------------------------------------------

    assistant_message = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=answer,
    )

    db.add(assistant_message)

    # --------------------------------------------------
    # 8. Update session timestamp
    # --------------------------------------------------

    session.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(assistant_message)

    # --------------------------------------------------
    # 9. Return complete response
    # --------------------------------------------------

    return {
        "session_id": session.id,

        "user_message": {
            "id": user_message.id,
            "role": user_message.role,
            "content": user_message.content,
            "created_at": user_message.created_at,
        },

        "assistant_message": {
            "id": assistant_message.id,
            "role": assistant_message.role,
            "content": assistant_message.content,
            "created_at": assistant_message.created_at,
        },

        "citations": citations,
    }


# ==================================================
# DELETE SESSION
# ==================================================

@router.delete("/{session_id}")
def delete_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = (
        db.query(ChatSession)
        .filter(
            ChatSession.id == session_id,
            ChatSession.workspace_id
            == current_user.workspace_id,
            ChatSession.user_id
            == current_user.id,
        )
        .first()
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    # --------------------------------------------------
    # Delete messages
    # --------------------------------------------------

    db.query(ChatMessage).filter(
        ChatMessage.session_id == session.id
    ).delete(
        synchronize_session=False
    )

    # --------------------------------------------------
    # Delete session
    # --------------------------------------------------

    db.delete(session)

    db.commit()

    return {
        "message": "Chat session deleted successfully.",
        "session_id": session_id,
    }
