from pydantic import BaseModel


class TranscriptSegmentOut(BaseModel):
    id: int
    speaker_label: str
    participant_name: str | None = None
    start_time: float
    end_time: float
    text: str
    confidence: float | None
    segment_order: int

    model_config = {"from_attributes": True}


class TranscriptOut(BaseModel):
    meeting_id: int
    segments: list[TranscriptSegmentOut]
    full_text: str
