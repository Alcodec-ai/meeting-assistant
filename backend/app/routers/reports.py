from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.report import ProgressReport
from app.schemas.report import ReportGenerate, ReportOut

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("", response_model=list[ReportOut])
async def list_reports(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProgressReport).order_by(ProgressReport.generated_at.desc())
    )
    return result.scalars().all()


@router.post("/generate", response_model=dict)
async def generate_report(data: ReportGenerate, db: AsyncSession = Depends(get_db)):
    from app.workers.tasks import generate_progress_report

    generate_progress_report.delay(
        meeting_id=data.meeting_id,
        report_type=data.report_type.value,
    )
    return {"message": "Rapor oluşturuluyor..."}


@router.get("/{report_id}", response_model=ReportOut)
async def get_report(report_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ProgressReport).where(ProgressReport.id == report_id)
    )
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Rapor bulunamadı")
    return report
