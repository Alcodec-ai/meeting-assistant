"""Celery background tasks for audio processing and LLM analysis."""

import asyncio
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from celery_app import celery

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async coroutine from synchronous Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(bind=True, max_retries=2)
def process_meeting_audio(self, meeting_id: int):
    """Full pipeline: diarize → transcribe → summarize → extract tasks."""
    try:
        _run_async(_process_meeting_audio(meeting_id))
    except Exception as exc:
        logger.exception("Failed to process meeting %d", meeting_id)
        _run_async(_set_meeting_failed(meeting_id))
        raise self.retry(exc=exc, countdown=60)


@celery.task
def regenerate_meeting_summary(meeting_id: int):
    """Regenerate summary and tasks for an already transcribed meeting."""
    _run_async(_regenerate_summary(meeting_id))


@celery.task
def generate_progress_report(meeting_id: int | None, report_type: str):
    """Generate a progress report."""
    _run_async(_generate_report(meeting_id, report_type))


async def _process_meeting_audio(meeting_id: int):
    from app.database import async_session
    from app.models.meeting import Meeting, MeetingStatus
    from app.models.participant import Participant
    from app.models.summary import Summary
    from app.models.task import Task, TaskPriority
    from app.models.transcript import TranscriptSegment
    from app.services.audio_processor import process_audio
    from app.services.summarizer import generate_summary
    from app.services.task_extractor import extract_tasks

    async with async_session() as db:
        result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = result.scalar_one()

        # Step 1: Audio processing (diarization + transcription)
        logger.info("Processing audio for meeting %d: %s", meeting_id, meeting.audio_file_path)
        segments = process_audio(meeting.audio_file_path)

        # Step 2: Save participants (unique speakers)
        speakers = set(seg["speaker"] for seg in segments)
        speaker_to_participant = {}
        for speaker in speakers:
            participant = Participant(
                meeting_id=meeting_id,
                name=speaker,
                speaker_label=speaker,
            )
            db.add(participant)
            await db.flush()
            speaker_to_participant[speaker] = participant

        # Step 3: Save transcript segments
        for i, seg in enumerate(segments):
            participant = speaker_to_participant[seg["speaker"]]
            db_seg = TranscriptSegment(
                meeting_id=meeting_id,
                participant_id=participant.id,
                speaker_label=seg["speaker"],
                start_time=seg["start"],
                end_time=seg["end"],
                text=seg["text"],
                segment_order=i,
            )
            db.add(db_seg)

        # Step 4: Calculate duration
        if segments:
            meeting.duration_seconds = int(segments[-1]["end"])

        await db.flush()

        # Step 5: Build full transcript text for LLM
        transcript_text = "\n".join(
            f"[{seg['speaker']}]: {seg['text']}" for seg in segments
        )
        participant_names = [p.name for p in speaker_to_participant.values()]

        # Step 6: LLM - Generate summary
        logger.info("Generating summary for meeting %d", meeting_id)
        summary_data = await generate_summary(transcript_text)
        summary = Summary(
            meeting_id=meeting_id,
            full_summary=summary_data.get("full_summary", ""),
            key_points=summary_data.get("key_points", []),
            decisions=summary_data.get("decisions", []),
        )
        db.add(summary)

        # Step 7: LLM - Extract tasks
        logger.info("Extracting tasks for meeting %d", meeting_id)
        tasks_data = await extract_tasks(transcript_text, participant_names)
        for task_data in tasks_data:
            # Try to match assignee to a participant
            assignee_id = None
            assignee_name = task_data.get("assignee")
            if assignee_name:
                for speaker, participant in speaker_to_participant.items():
                    if participant.name == assignee_name:
                        assignee_id = participant.id
                        break

            priority_str = task_data.get("priority", "medium")
            try:
                priority = TaskPriority(priority_str)
            except ValueError:
                priority = TaskPriority.MEDIUM

            task = Task(
                meeting_id=meeting_id,
                assignee_id=assignee_id,
                title=task_data.get("title", ""),
                description=task_data.get("description"),
                priority=priority,
            )
            db.add(task)

        # Step 8: Mark as completed
        meeting.status = MeetingStatus.COMPLETED
        await db.commit()
        logger.info("Meeting %d processing completed", meeting_id)


async def _set_meeting_failed(meeting_id: int):
    from app.database import async_session
    from app.models.meeting import Meeting, MeetingStatus

    async with async_session() as db:
        result = await db.execute(select(Meeting).where(Meeting.id == meeting_id))
        meeting = result.scalar_one()
        meeting.status = MeetingStatus.FAILED
        await db.commit()


async def _regenerate_summary(meeting_id: int):
    from app.database import async_session
    from app.models.summary import Summary
    from app.models.transcript import TranscriptSegment
    from app.services.summarizer import generate_summary

    async with async_session() as db:
        result = await db.execute(
            select(TranscriptSegment)
            .where(TranscriptSegment.meeting_id == meeting_id)
            .order_by(TranscriptSegment.segment_order)
        )
        segments = result.scalars().all()
        transcript_text = "\n".join(
            f"[{seg.speaker_label}]: {seg.text}" for seg in segments
        )

        summary_data = await generate_summary(transcript_text)

        # Update or create summary
        result = await db.execute(
            select(Summary).where(Summary.meeting_id == meeting_id)
        )
        summary = result.scalar_one_or_none()
        if summary:
            summary.full_summary = summary_data.get("full_summary", "")
            summary.key_points = summary_data.get("key_points", [])
            summary.decisions = summary_data.get("decisions", [])
        else:
            summary = Summary(
                meeting_id=meeting_id,
                full_summary=summary_data.get("full_summary", ""),
                key_points=summary_data.get("key_points", []),
                decisions=summary_data.get("decisions", []),
            )
            db.add(summary)

        await db.commit()


async def _generate_report(meeting_id: int | None, report_type: str):
    from app.database import async_session
    from app.models.meeting import Meeting
    from app.models.report import ProgressReport, ReportType
    from app.models.summary import Summary
    from app.models.task import Task
    from app.services.report_generator import generate_meeting_report

    async with async_session() as db:
        if meeting_id:
            result = await db.execute(
                select(Meeting).where(Meeting.id == meeting_id)
            )
            meeting = result.scalar_one()

            result = await db.execute(
                select(Summary).where(Summary.meeting_id == meeting_id)
            )
            summary = result.scalar_one_or_none()

            result = await db.execute(
                select(Task)
                .options(selectinload(Task.assignee))
                .where(Task.meeting_id == meeting_id)
            )
            tasks = result.scalars().all()

            summary_dict = {
                "full_summary": summary.full_summary if summary else "",
                "key_points": summary.key_points if summary else [],
            }
            tasks_list = [
                {
                    "title": t.title,
                    "status": t.status.value,
                    "priority": t.priority.value,
                    "assignee_name": t.assignee.name if t.assignee else "Atanmamış",
                }
                for t in tasks
            ]

            content = await generate_meeting_report(
                summary_dict, tasks_list, meeting.title
            )
        else:
            content = {"message": "Genel rapor henüz desteklenmiyor"}

        report = ProgressReport(
            meeting_id=meeting_id,
            report_type=ReportType(report_type),
            content=content,
        )
        db.add(report)
        await db.commit()
