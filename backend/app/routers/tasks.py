from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models.task import Task, TaskStatus
from app.schemas.task import TaskCreate, TaskOut, TaskUpdate

router = APIRouter(tags=["tasks"])


def _task_to_out(task: Task) -> TaskOut:
    return TaskOut(
        id=task.id,
        meeting_id=task.meeting_id,
        assignee_id=task.assignee_id,
        assignee_name=task.assignee.name if task.assignee else None,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        due_date=task.due_date,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


@router.get("/api/meetings/{meeting_id}/tasks", response_model=list[TaskOut])
async def get_meeting_tasks(meeting_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Task)
        .options(selectinload(Task.assignee))
        .where(Task.meeting_id == meeting_id)
        .order_by(Task.created_at)
    )
    return [_task_to_out(t) for t in result.scalars().all()]


@router.get("/api/tasks", response_model=list[TaskOut])
async def list_all_tasks(
    status: TaskStatus | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).options(selectinload(Task.assignee)).order_by(Task.created_at)
    if status:
        query = query.where(Task.status == status)
    result = await db.execute(query)
    return [_task_to_out(t) for t in result.scalars().all()]


@router.post("/api/meetings/{meeting_id}/tasks", response_model=TaskOut, status_code=201)
async def create_task(
    meeting_id: int,
    data: TaskCreate,
    db: AsyncSession = Depends(get_db),
):
    task = Task(
        meeting_id=meeting_id,
        title=data.title,
        description=data.description,
        assignee_id=data.assignee_id,
        priority=data.priority,
        due_date=data.due_date,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task, ["assignee"])
    return _task_to_out(task)


@router.put("/api/tasks/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task).options(selectinload(Task.assignee)).where(Task.id == task_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Görev bulunamadı")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task, ["assignee"])
    return _task_to_out(task)
