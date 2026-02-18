import os
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config import settings
from app.database import get_db
from app.models.meeting import Meeting, MeetingStatus
from app.models.participant import Participant
from app.schemas.meeting import (
    MeetingCreate,
    MeetingDetail,
    MeetingOut,
    ParticipantOut,
    ParticipantUpdate,
)

router = APIRouter(prefix="/api/meetings", tags=["meetings"])


@router.post("", response_model=MeetingOut, status_code=201)
async def create_meeting(data: MeetingCreate, db: AsyncSession = Depends(get_db)):
    meeting = Meeting(title=data.title, description=data.description)
    if data.date:
        meeting.date = data.date
    db.add(meeting)
    await db.commit()
    await db.refresh(meeting)
    return meeting


@router.get("", response_model=list[MeetingOut])
async def list_meetings(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).order_by(Meeting.created_at.desc()))
    return result.scalars().all()


@router.get("/{meeting_id}", response_model=MeetingDetail)
async def get_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Meeting)
        .options(selectinload(Meeting.participants))
        .where(Meeting.id == meeting_id)
    )
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")
    return meeting


@router.delete("/{meeting_id}", status_code=204)
async def delete_meeting(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")
    await db.delete(meeting)
    await db.commit()


@router.post("/{meeting_id}/upload", response_model=MeetingOut)
async def upload_audio(
    meeting_id: int,
    file: UploadFile,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")

    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)

    ext = os.path.splitext(file.filename or "audio.wav")[1]
    file_path = upload_dir / f"meeting_{meeting_id}{ext}"

    content = await file.read()
    file_path.write_bytes(content)

    meeting.audio_file_path = str(file_path)
    meeting.status = MeetingStatus.PROCESSING
    await db.commit()
    await db.refresh(meeting)

    # Trigger background processing
    from app.workers.tasks import process_meeting_audio

    process_meeting_audio.delay(meeting_id)

    return meeting


@router.get("/{meeting_id}/status")
async def get_meeting_status(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")
    return {"status": meeting.status}


@router.get("/{meeting_id}/participants", response_model=list[ParticipantOut])
async def get_participants(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Participant).where(Participant.meeting_id == meeting_id)
    )
    return result.scalars().all()


@router.put("/{meeting_id}/participants/{participant_id}", response_model=ParticipantOut)
async def update_participant(
    meeting_id: int,
    participant_id: int,
    data: ParticipantUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Participant).where(
            Participant.id == participant_id,
            Participant.meeting_id == meeting_id,
        )
    )
    participant = result.scalar_one_or_none()
    if not participant:
        raise HTTPException(status_code=404, detail="Katılımcı bulunamadı")

    if data.name is not None:
        participant.name = data.name
    if data.email is not None:
        participant.email = data.email

    await db.commit()
    await db.refresh(participant)
    return participant
