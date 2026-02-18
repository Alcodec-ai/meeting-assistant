from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.meeting import Meeting
from app.models.summary import Summary
from app.models.transcript import TranscriptSegment
from app.schemas.report import SummaryOut
from app.schemas.transcript import TranscriptOut, TranscriptSegmentOut

router = APIRouter(prefix="/api/meetings", tags=["transcripts"])


@router.get("/{meeting_id}/transcript", response_model=TranscriptOut)
async def get_transcript(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")

    result = await db.execute(
        select(TranscriptSegment)
        .options(selectinload(TranscriptSegment.participant))
        .where(TranscriptSegment.meeting_id == meeting_id)
        .order_by(TranscriptSegment.segment_order)
    )
    segments = result.scalars().all()

    segment_outs = []
    full_parts = []
    for seg in segments:
        name = seg.participant.name if seg.participant else seg.speaker_label
        segment_outs.append(
            TranscriptSegmentOut(
                id=seg.id,
                speaker_label=seg.speaker_label,
                participant_name=name,
                start_time=seg.start_time,
                end_time=seg.end_time,
                text=seg.text,
                confidence=seg.confidence,
                segment_order=seg.segment_order,
            )
        )
        full_parts.append(f"[{name}]: {seg.text}")

    return TranscriptOut(
        meeting_id=meeting_id,
        segments=segment_outs,
        full_text="\n".join(full_parts),
    )


@router.get("/{meeting_id}/summary", response_model=SummaryOut)
async def get_summary(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Summary).where(Summary.meeting_id == meeting_id)
    )
    summary = result.scalar_one_or_none()
    if not summary:
        raise HTTPException(status_code=404, detail="Özet henüz oluşturulmamış")
    return summary


@router.post("/{meeting_id}/summary/regenerate", response_model=SummaryOut)
async def regenerate_summary(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
    meeting = result.scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=404, detail="Toplantı bulunamadı")

    from app.workers.tasks import regenerate_meeting_summary

    regenerate_meeting_summary.delay(meeting_id)
    return {"message": "Özet yeniden oluşturuluyor..."}
