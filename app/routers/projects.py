from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectRead, ProjectCreate
from app.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("",response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, db: Annotated[Session, Depends(get_db)],
                   me: Annotated[User, Depends(get_current_user)]):
    exists = (db.query(Project).filter(Project.name == payload.name, Project.owner_id == me.id).first())
    if exists:
        raise HTTPException(status_code=409, detail="The project name is already taken")
    project = Project(name = payload.name, desc = payload.desc, owner_id = me.id)
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@router.get("", response_model=list[ProjectRead], dependencies=[Depends(get_current_user)])
def list_projects(db: Annotated[Session, Depends(get_db)],
                  skip: int = Query(0, ge=0),
                  limit: int = Query(50, ge=1, le=100),
                  q: str | None = Query(None, description="Filter by name (icontains)"),
                  sort_by: Literal["id", "name", "owner_id"] = "id",
                  sort_dir: Literal["asc", "desc"] = "asc") -> list[ProjectRead]:
    query = db.query(Project)
    if q:
        query = query.filter(Project.name.ilike(f"%{q}%"))
    col = getattr(Project, sort_by)
    order = asc(col) if sort_dir == "asc" else desc(col)
    query = query.order_by(order)
    projects = query.offset(skip).limit(limit).all()
    return projects

@router.get("/{project_id}", response_model=ProjectRead)
def get_one_project(project_id: int, db: Annotated[Session, Depends(get_db)]):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    return p

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Annotated[Session, Depends(get_db)],
                   user: Annotated[User, Depends(get_current_user)]):
    p = db.get(Project, project_id)
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")
    if p.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Only project owner can delete a project")
    db.delete(p)
    db.commit()
    return