from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ProjectCreate(BaseModel):
    name: str
    desc: str = ""


class ProjectRead(ProjectCreate):
    id: int
    created_at: datetime
    owner_id: int

    model_config = ConfigDict(from_attributes=True)
