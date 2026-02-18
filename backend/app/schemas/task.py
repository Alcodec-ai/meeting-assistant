from datetime import date, datetime

from pydantic import BaseModel

from app.models.task import TaskPriority, TaskStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    assignee_id: int | None = None
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    assignee_id: int | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    due_date: date | None = None


class TaskOut(BaseModel):
    id: int
    meeting_id: int
    assignee_id: int | None
    assignee_name: str | None = None
    title: str
    description: str | None
    priority: TaskPriority
    status: TaskStatus
    due_date: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
