from datetime import datetime

from pydantic import BaseModel

from app.models.report import ReportType


class ReportGenerate(BaseModel):
    meeting_id: int | None = None
    report_type: ReportType = ReportType.MEETING


class ReportOut(BaseModel):
    id: int
    meeting_id: int | None
    report_type: ReportType
    content: dict
    generated_at: datetime

    model_config = {"from_attributes": True}


class SummaryOut(BaseModel):
    id: int
    meeting_id: int
    full_summary: str
    key_points: list
    decisions: list
    created_at: datetime

    model_config = {"from_attributes": True}
