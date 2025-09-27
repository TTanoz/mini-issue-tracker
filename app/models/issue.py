from datetime import datetime
from enum import Enum
from sqlalchemy import String, DateTime, func, Text, ForeignKey, UniqueConstraint,Enum as MyEnum
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base

class IssueStatus(str, Enum):
    open = "open"
    closed = "closed"

class IssuePriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class Issue(Base):
    __tablename__ = "issues"
    __table_args__ = (
        UniqueConstraint("title", "project_id", name="uq_title_name_project_id"),
    )


    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    desc: Mapped[str] = mapped_column(Text, nullable= True, server_default="", default="")
    status: Mapped[IssueStatus] = mapped_column(MyEnum(IssueStatus, name = "status", validate_strings = True), nullable=False, default=IssueStatus.open)
    priority: Mapped[IssuePriority] = mapped_column(MyEnum(IssuePriority, name = "priority", validate_strings = True), nullable=False, default=IssuePriority.medium)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate= func.now())
    project_id : Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"), index=True, nullable=False)
    reporter_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    assignee_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=True)