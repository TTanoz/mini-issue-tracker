from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime

class CommentCreate(BaseModel):
    content: str

    @field_validator("content")
    @classmethod
    def _content_not_empty(cls, c: str) -> str:
        c2 = c.strip()
        if not c2:
            raise ValueError("Content cannot be empty")
        return c2

class CommentRead(CommentCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    issue_id: int
    author_id: int

    model_config = ConfigDict(from_attributes=True)