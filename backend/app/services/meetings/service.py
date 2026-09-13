from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.meeting import (
    Meeting,
    MeetingParticipant,
    MeetingTranscript,
    MeetingDecision,
    MeetingActionItem,
    MeetingSummary,
)


class MeetingService:

    # ========================================================
    # MEETING
    # ========================================================

    def create_meeting(
        self,
        db: Session,
        title: str,
        description: str | None = None,
        meeting_type: str | None = None,
        source_type: str = "upload",
        source_uri: str | None = None,
    ) -> Meeting:

        meeting = Meeting(
            title=title,
            description=description,
            meeting_type=meeting_type,
            source_type=source_type,
            source_uri=source_uri,
            status="pending",
        )

        db.add(meeting)
        db.commit()
        db.refresh(meeting)

        return meeting

    def get_meeting(
        self,
        db: Session,
        meeting_id: int,
    ) -> Meeting | None:

        return (
            db.query(Meeting)
            .filter(Meeting.id == meeting_id)
            .first()
        )

    def list_meetings(
        self,
        db: Session,
        limit: int = 50,
    ) -> list[Meeting]:

        return (
            db.query(Meeting)
            .order_by(Meeting.created_at.desc())
            .limit(limit)
            .all()
        )

    def update_status(
        self,
        db: Session,
        meeting_id: int,
        status: str,
    ) -> Meeting:

        meeting = self.get_meeting(db, meeting_id)

        if not meeting:
            raise ValueError("Meeting not found")

        meeting.status = status

        if status == "processing":
            meeting.started_at = datetime.utcnow()

        if status in {
            "completed",
            "failed",
        }:
            meeting.ended_at = datetime.utcnow()

            if meeting.started_at:
                meeting.duration_seconds = int(
                    (
                        meeting.ended_at
                        - meeting.started_at
                    ).total_seconds()
                )

        db.commit()
        db.refresh(meeting)

        return meeting

    # ========================================================
    # PARTICIPANTS
    # ========================================================

    def add_participant(
        self,
        db: Session,
        meeting_id: int,
        name: str,
        email: str | None = None,
        speaker_label: str | None = None,
        user_id: int | None = None,
    ) -> MeetingParticipant:

        participant = MeetingParticipant(
            meeting_id=meeting_id,
            name=name,
            email=email,
            speaker_label=speaker_label,
            user_id=user_id,
        )

        db.add(participant)
        db.commit()
        db.refresh(participant)

        return participant

    def list_participants(
        self,
        db: Session,
        meeting_id: int,
    ) -> list[MeetingParticipant]:

        return (
            db.query(MeetingParticipant)
            .filter(
                MeetingParticipant.meeting_id
                == meeting_id
            )
            .all()
        )

    # ========================================================
    # TRANSCRIPT
    # ========================================================

    def add_transcript(
        self,
        db: Session,
        meeting_id: int,
        text: str,
        sequence_number: int,
        speaker_label: str | None = None,
        participant_id: int | None = None,
        start_time_seconds: float | None = None,
        end_time_seconds: float | None = None,
    ) -> MeetingTranscript:

        transcript = MeetingTranscript(
            meeting_id=meeting_id,
            speaker_label=speaker_label,
            participant_id=participant_id,
            start_time_seconds=start_time_seconds,
            end_time_seconds=end_time_seconds,
            text=text,
            sequence_number=sequence_number,
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        return transcript

    def get_transcript(
        self,
        db: Session,
        meeting_id: int,
    ) -> list[MeetingTranscript]:

        return (
            db.query(MeetingTranscript)
            .filter(
                MeetingTranscript.meeting_id
                == meeting_id
            )
            .order_by(
                MeetingTranscript.sequence_number.asc()
            )
            .all()
        )

    # ========================================================
    # DECISIONS
    # ========================================================

    def add_decision(
        self,
        db: Session,
        meeting_id: int,
        decision: str,
        context: str | None = None,
        speaker_label: str | None = None,
    ) -> MeetingDecision:

        item = MeetingDecision(
            meeting_id=meeting_id,
            decision=decision,
            context=context,
            speaker_label=speaker_label,
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def get_decisions(
        self,
        db: Session,
        meeting_id: int,
    ) -> list[MeetingDecision]:

        return (
            db.query(MeetingDecision)
            .filter(
                MeetingDecision.meeting_id
                == meeting_id
            )
            .all()
        )

    # ========================================================
    # ACTION ITEMS
    # ========================================================

    def add_action_item(
        self,
        db: Session,
        meeting_id: int,
        description: str,
        assignee_name: str | None = None,
        assignee_user_id: int | None = None,
        due_at: datetime | None = None,
    ) -> MeetingActionItem:

        item = MeetingActionItem(
            meeting_id=meeting_id,
            description=description,
            assignee_name=assignee_name,
            assignee_user_id=assignee_user_id,
            due_at=due_at,
            status="pending",
        )

        db.add(item)
        db.commit()
        db.refresh(item)

        return item

    def get_action_items(
        self,
        db: Session,
        meeting_id: int,
    ) -> list[MeetingActionItem]:

        return (
            db.query(MeetingActionItem)
            .filter(
                MeetingActionItem.meeting_id
                == meeting_id
            )
            .order_by(
                MeetingActionItem.created_at.asc()
            )
            .all()
        )

    def update_action_status(
        self,
        db: Session,
        action_id: int,
        status: str,
    ) -> MeetingActionItem:

        item = (
            db.query(MeetingActionItem)
            .filter(
                MeetingActionItem.id
                == action_id
            )
            .first()
        )

        if not item:
            raise ValueError(
                "Action item not found"
            )

        item.status = status
        db.commit()
        db.refresh(item)

        return item

    # ========================================================
    # SUMMARY
    # ========================================================

    def save_summary(
        self,
        db: Session,
        meeting_id: int,
        summary: str,
        key_points: str | None = None,
        follow_ups: str | None = None,
        generated_by: str | None = "system",
    ) -> MeetingSummary:

        existing = (
            db.query(MeetingSummary)
            .filter(
                MeetingSummary.meeting_id
                == meeting_id
            )
            .first()
        )

        if existing:

            existing.summary = summary
            existing.key_points = key_points
            existing.follow_ups = follow_ups
            existing.generated_by = generated_by

            db.commit()
            db.refresh(existing)

            return existing

        result = MeetingSummary(
            meeting_id=meeting_id,
            summary=summary,
            key_points=key_points,
            follow_ups=follow_ups,
            generated_by=generated_by,
        )

        db.add(result)
        db.commit()
        db.refresh(result)

        return result

    def get_summary(
        self,
        db: Session,
        meeting_id: int,
    ) -> MeetingSummary | None:

        return (
            db.query(MeetingSummary)
            .filter(
                MeetingSummary.meeting_id
                == meeting_id
            )
            .first()
        )

    # ========================================================
    # COMPLETE MEETING VIEW
    # ========================================================

    def get_full_meeting(
        self,
        db: Session,
        meeting_id: int,
    ) -> dict[str, Any]:

        meeting = self.get_meeting(
            db,
            meeting_id,
        )

        if not meeting:
            raise ValueError(
                "Meeting not found"
            )

        participants = self.list_participants(
            db,
            meeting_id,
        )

        transcript = self.get_transcript(
            db,
            meeting_id,
        )

        decisions = self.get_decisions(
            db,
            meeting_id,
        )

        action_items = self.get_action_items(
            db,
            meeting_id,
        )

        summary = self.get_summary(
            db,
            meeting_id,
        )

        return {
            "meeting": meeting,
            "participants": participants,
            "transcript": transcript,
            "decisions": decisions,
            "action_items": action_items,
            "summary": summary,
        }


meeting_service = MeetingService()
