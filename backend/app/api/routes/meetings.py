from datetime import datetime
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.database.database import SessionLocal
from app.models.meeting import (
    Meeting,
    MeetingParticipant,
    MeetingTranscript,
    MeetingDecision,
    MeetingActionItem,
    MeetingSummary,
)


router = APIRouter(
    prefix="/meetings",
    tags=["Meetings"],
)


# ============================================================
# REQUEST MODELS
# ============================================================

class MeetingCreate(BaseModel):
    title: str
    description: str | None = None
    meeting_type: str | None = None
    source_type: str = "upload"
    source_uri: str | None = None


class ParticipantCreate(BaseModel):
    name: str
    email: str | None = None
    speaker_label: str | None = None
    user_id: int | None = None


class TranscriptCreate(BaseModel):
    speaker_label: str | None = None
    participant_id: int | None = None
    start_time_seconds: float | None = None
    end_time_seconds: float | None = None
    text: str
    sequence_number: int


class DecisionCreate(BaseModel):
    decision: str
    context: str | None = None
    speaker_label: str | None = None


class ActionItemCreate(BaseModel):
    description: str
    assignee_name: str | None = None
    assignee_user_id: int | None = None
    due_at: datetime | None = None


class SummaryCreate(BaseModel):
    summary: str
    key_points: str | None = None
    follow_ups: str | None = None
    generated_by: str | None = "company-os"


class MeetingStatusUpdate(BaseModel):
    status: str = Field(
        ...,
        description="pending, processing, completed, failed",
    )


# ============================================================
# CREATE MEETING
# ============================================================

@router.post("")
def create_meeting(request: MeetingCreate):
    db = SessionLocal()

    try:
        meeting = Meeting(
            title=request.title,
            description=request.description,
            meeting_type=request.meeting_type,
            source_type=request.source_type,
            source_uri=request.source_uri,
            status="pending",
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        return {
            "id": meeting.id,
            "title": meeting.title,
            "status": meeting.status,
            "source_type": meeting.source_type,
            "created_at": meeting.created_at,
        }

    finally:
        db.close()


# ============================================================
# LIST MEETINGS
# ============================================================

@router.get("")
def list_meetings():
    db = SessionLocal()

    try:
        meetings = (
            db.query(Meeting)
            .order_by(Meeting.created_at.desc())
            .all()
        )

        return {
            "meetings": [
                {
                    "id": meeting.id,
                    "title": meeting.title,
                    "meeting_type": meeting.meeting_type,
                    "source_type": meeting.source_type,
                    "status": meeting.status,
                    "started_at": meeting.started_at,
                    "ended_at": meeting.ended_at,
                    "duration_seconds": meeting.duration_seconds,
                    "created_at": meeting.created_at,
                }
                for meeting in meetings
            ]
        }

    finally:
        db.close()


# ============================================================
# GET MEETING
# ============================================================

@router.get("/{meeting_id}")
def get_meeting(meeting_id: int):
    db = SessionLocal()

    try:
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found",
            )

        participants = (
            db.query(MeetingParticipant)
            .filter(
                MeetingParticipant.meeting_id == meeting_id
            )
            .all()
        )

        transcripts = (
            db.query(MeetingTranscript)
            .filter(
                MeetingTranscript.meeting_id == meeting_id
            )
            .order_by(
                MeetingTranscript.sequence_number
            )
            .all()
        )

        decisions = (
            db.query(MeetingDecision)
            .filter(
                MeetingDecision.meeting_id == meeting_id
            )
            .all()
        )

        action_items = (
            db.query(MeetingActionItem)
            .filter(
                MeetingActionItem.meeting_id == meeting_id
            )
            .all()
        )

        summary = (
            db.query(MeetingSummary)
            .filter(
                MeetingSummary.meeting_id == meeting_id
            )
            .first()
        )

        return {
            "meeting": {
                "id": meeting.id,
                "title": meeting.title,
                "description": meeting.description,
                "meeting_type": meeting.meeting_type,
                "source_type": meeting.source_type,
                "source_uri": meeting.source_uri,
                "status": meeting.status,
                "started_at": meeting.started_at,
                "ended_at": meeting.ended_at,
                "duration_seconds": meeting.duration_seconds,
                "created_at": meeting.created_at,
            },

            "participants": [
                {
                    "id": p.id,
                    "name": p.name,
                    "email": p.email,
                    "speaker_label": p.speaker_label,
                    "user_id": p.user_id,
                    "joined_at": p.joined_at,
                    "left_at": p.left_at,
                }
                for p in participants
            ],

            "transcript": [
                {
                    "id": t.id,
                    "speaker_label": t.speaker_label,
                    "participant_id": t.participant_id,
                    "start_time_seconds": t.start_time_seconds,
                    "end_time_seconds": t.end_time_seconds,
                    "text": t.text,
                    "sequence_number": t.sequence_number,
                }
                for t in transcripts
            ],

            "decisions": [
                {
                    "id": d.id,
                    "decision": d.decision,
                    "context": d.context,
                    "speaker_label": d.speaker_label,
                }
                for d in decisions
            ],

            "action_items": [
                {
                    "id": a.id,
                    "description": a.description,
                    "assignee_name": a.assignee_name,
                    "assignee_user_id": a.assignee_user_id,
                    "due_at": a.due_at,
                    "status": a.status,
                }
                for a in action_items
            ],

            "summary": (
                {
                    "id": summary.id,
                    "summary": summary.summary,
                    "key_points": summary.key_points,
                    "follow_ups": summary.follow_ups,
                    "generated_by": summary.generated_by,
                }
                if summary
                else None
            ),
        }

    finally:
        db.close()


# ============================================================
# UPDATE STATUS
# ============================================================

@router.patch("/{meeting_id}/status")
def update_meeting_status(
    meeting_id: int,
    request: MeetingStatusUpdate,
):
    db = SessionLocal()

    try:
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found",
            )

        allowed = {
            "pending",
            "processing",
            "completed",
            "failed",
        }

        if request.status not in allowed:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {sorted(allowed)}",
            )

        meeting.status = request.status

        db.commit()
        db.refresh(meeting)

        return {
            "id": meeting.id,
            "status": meeting.status,
        }

    finally:
        db.close()


# ============================================================
# ADD PARTICIPANT
# ============================================================

@router.post("/{meeting_id}/participants")
def add_participant(
    meeting_id: int,
    request: ParticipantCreate,
):
    db = SessionLocal()

    try:
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found",
            )

        participant = MeetingParticipant(
            meeting_id=meeting_id,
            name=request.name,
            email=request.email,
            speaker_label=request.speaker_label,
            user_id=request.user_id,
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        return {
            "id": participant.id,
            "meeting_id": participant.meeting_id,
            "name": participant.name,
            "email": participant.email,
            "speaker_label": participant.speaker_label,
        }

    finally:
        db.close()


# ============================================================
# ADD TRANSCRIPT SEGMENT
# ============================================================

@router.post("/{meeting_id}/transcript")
def add_transcript(
    meeting_id: int,
    request: TranscriptCreate,
):
    db = SessionLocal()

    try:
        meeting = (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

        if not meeting:
            raise HTTPException(
                status_code=404,
                detail="Meeting not found",
            )

        transcript = MeetingTranscript(
            meeting_id=meeting_id,
            speaker_label=request.speaker_label,
            participant_id=request.participant_id,
            start_time_seconds=request.start_time_seconds,
            end_time_seconds=request.end_time_seconds,
            text=request.text,
            sequence_number=request.sequence_number,
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        return {
            "id": transcript.id,
            "meeting_id": transcript.meeting_id,
            "speaker_label": transcript.speaker_label,
            "start_time_seconds": transcript.start_time_seconds,
            "end_time_seconds": transcript.end_time_seconds,
            "text": transcript.text,
            "sequence_number": transcript.sequence_number,
        }

    finally:
        db.close()


# ============================================================
# ADD DECISION
# ============================================================

@router.post("/{meeting_id}/decisions")
def add_decision(
    meeting_id: int,
    request: DecisionCreate,
):
    db = SessionLocal()

    try:
        decision = MeetingDecision(
            meeting_id=meeting_id,
            decision=request.decision,
            context=request.context,
            speaker_label=request.speaker_label,
        )

        db.add(decision)
        db.commit()
        db.refresh(decision)

        return {
            "id": decision.id,
            "meeting_id": meeting_id,
            "decision": decision.decision,
            "context": decision.context,
        }

    finally:
        db.close()


# ============================================================
# ADD ACTION ITEM
# ============================================================

@router.post("/{meeting_id}/action-items")
def add_action_item(
    meeting_id: int,
    request: ActionItemCreate,
):
    db = SessionLocal()

    try:
        action = MeetingActionItem(
            meeting_id=meeting_id,
            description=request.description,
            assignee_name=request.assignee_name,
            assignee_user_id=request.assignee_user_id,
            due_at=request.due_at,
            status="pending",
        )

        db.add(action)
        db.commit()
        db.refresh(action)

        return {
            "id": action.id,
            "meeting_id": meeting_id,
            "description": action.description,
            "assignee_name": action.assignee_name,
            "due_at": action.due_at,
            "status": action.status,
        }

    finally:
        db.close()


# ============================================================
# ADD / UPDATE SUMMARY
# ============================================================

@router.put("/{meeting_id}/summary")
def save_summary(
    meeting_id: int,
    request: SummaryCreate,
):
    db = SessionLocal()

    try:
        summary = (
            db.query(MeetingSummary)
            .filter(
                MeetingSummary.meeting_id == meeting_id
            )
            .first()
        )

        if summary:
            summary.summary = request.summary
            summary.key_points = request.key_points
            summary.follow_ups = request.follow_ups
            summary.generated_by = request.generated_by

        else:
            summary = MeetingSummary(
                meeting_id=meeting_id,
                summary=request.summary,
                key_points=request.key_points,
                follow_ups=request.follow_ups,
                generated_by=request.generated_by,
            )

            db.add(summary)

        db.commit()
        db.refresh(summary)

        return {
            "id": summary.id,
            "meeting_id": summary.meeting_id,
            "summary": summary.summary,
            "key_points": summary.key_points,
            "follow_ups": summary.follow_ups,
            "generated_by": summary.generated_by,
        }

    finally:
        db.close()
