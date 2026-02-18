from datetime import datetime

from pydantic import BaseModel

from app.models.meeting import MeetingStatus


class MeetingCreate(BaseModel):
    title: str
    description: str | None = None
    date: datetime | None = None


class ParticipantOut(BaseModel):
    id: int
    name: str
    email: str | None
    speaker_label: str | None

    model_config = {"from_attributes": True}


class ParticipantUpdate(BaseModel):
    name: str | None = None
    email: str | None = None


class MeetingOut(BaseModel):
    id: int
    title: str
    description: str | None
    date: datetime
    duration_seconds: int | None
    status: MeetingStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MeetingDetail(MeetingOut):
    participants: list[ParticipantOut] = []
