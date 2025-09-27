from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.issue import IssuePriority, IssueStatus

class IssueCreate(BaseModel):
    title: str
    desc: str = ""
    status: IssueStatus = IssueStatus.open
    priority: IssuePriority = IssuePriority.medium
    assignee_id: int | None = None

class IssueUpdate(BaseModel):
    title: str | None = None
    desc: str | None = None
    status: IssueStatus | None = None
    priority: IssuePriority | None = None
    assignee_id: int | None = None

class IssueRead(IssueCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    project_id: int
    reporter_id: int
    

    model_config = ConfigDict(from_attributes=True)

