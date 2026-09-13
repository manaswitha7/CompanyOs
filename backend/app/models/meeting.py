from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    Float,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.database import Base


class Meeting(Base):
    """
    Represents a meeting in Company OS.

    A meeting can originate from:
        - uploaded audio/video
        - external meeting systems
        - future calendar integrations
    """

    __tablename__ = "meetings"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    meeting_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    source_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        default="upload",
    )

    source_uri: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    ended_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    duration_seconds: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class MeetingParticipant(Base):
    """
    Represents a participant in a meeting.

    A participant may eventually be linked to
    a Company OS user/person after entity resolution.
    """

    __tablename__ = "meeting_participants"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    email: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    speaker_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    joined_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    left_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class MeetingTranscript(Base):
    """
    Stores the transcript generated from a meeting.

    The transcript can later be chunked and embedded
    into the Company OS knowledge system.
    """

    __tablename__ = "meeting_transcripts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    speaker_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    participant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "meeting_participants.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    start_time_seconds: Mapped[float | None] = mapped_column(
        Float,
        nullable=True,
    )


end_time_seconds: Mapped[float | None] = mapped_column(
    Float,
    nullable=True,
)

text: Mapped[str] = mapped_column(
    Text,
    nullable=False,
)

sequence_number: Mapped[int] = mapped_column(
    Integer,
    nullable=False,
)

created_at: Mapped[datetime] = mapped_column(
    DateTime,
    default=datetime.utcnow,
    nullable=False,
)


class MeetingDecision(Base):
    """
    A decision extracted from a meeting.
    """

    __tablename__ = "meeting_decisions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    decision: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    context: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    speaker_label: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


class MeetingActionItem(Base):
    """
    An action item extracted from a meeting.
    """

    __tablename__ = "meeting_action_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    assignee_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    assignee_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey(
            "users.id",
            ondelete="SET NULL",
        ),
        nullable=True,
        index=True,
    )

    due_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class MeetingSummary(Base):
    """
    AI-generated summary of a meeting.
    """

    __tablename__ = "meeting_summaries"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    meeting_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "meetings.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    key_points: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    follow_ups: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    generated_by: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )
