from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.db.session import get_db
from app.models.user import User
from app.models.project import Project
from app.models.issue import Issue
from app.schemas.issue import IssueCreate, IssueRead, IssueUpdate
from app.deps import get_current_user

routerprojectissue = APIRouter(prefix="/projects", tags=["project_issues"])
router = APIRouter(prefix="/issues", tags=["issues"])

@routerprojectissue.post("/{project_id}/issues",response_model=IssueRead, status_code=status.HTTP_201_CREATED)
def create_issue(project_id: int, payload: IssueCreate, db: Annotated[Session, Depends(get_db)],
                 me: Annotated[User, Depends(get_current_user)]):
    if not db.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    exists = (db.query(Issue).filter(Issue.title == payload.title, Issue.project_id == project_id).first())
    if exists:
        raise HTTPException(status_code=409, detail="The issue title is already taken")
    issue = Issue(title = payload.title, desc = payload.desc, status = payload.status, priority = payload.priority,
                  project_id = project_id, reporter_id = me.id, assignee_id = payload.assignee_id)
    db.add(issue);db.commit();db.refresh(issue)
    return issue
@routerprojectissue.get("/{project_id}/issues",response_model=list[IssueRead],dependencies=[Depends(get_current_user)])
def list_project_issues(
    project_id: int,
    db: Annotated[Session, Depends(get_db)],
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    q: str | None = Query(None, description="Filter by issue title (icontains)"),
    sort_by: Literal["id", "title", "status", "priority", "created_at", "updated_at", "assignee_id", "reporter_id"] = "id",
    sort_dir: Literal["asc", "desc"] = "asc",
) -> list[IssueRead]:
    if not db.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    query = db.query(Issue).filter(Issue.project_id == project_id)
    if q:
        query = query.filter(Issue.title.ilike(f"%{q}%"))
    col = getattr(Issue, sort_by)
    order = asc(col) if sort_dir == "asc" else desc(col)
    query = query.order_by(order)
    issues = query.offset(skip).limit(limit).all()
    return issues

@router.get("/{issue_id}", response_model=IssueRead)
def get_issue(issue_id: int, db: Annotated[Session, Depends(get_db)]):
    i = db.get(Issue, issue_id)
    if not i:
        raise HTTPException(status_code=404, detail="Issue not found")
    return i

@router.patch("/{issue_id}", response_model=IssueRead)
def patch_issue(issue_id: int, payload: IssueUpdate, db: Annotated[Session, Depends(get_db)],
                me: Annotated[User, Depends(get_current_user)]):
    i = db.get(Issue, issue_id)
    if not i:
        raise HTTPException(status_code=404, detail="Issue not found")
    if i.reporter_id != me.id:
        raise HTTPException(status_code=403, detail="Now allowed")
    if payload.title is not None and payload.title != i.title:
        exists = (
            db.query(Issue)
            .filter(
                Issue.project_id == i.project_id,
                Issue.title == payload.title,
                Issue.id != i.id,
            )
            .first()
        )
        if exists:
            raise HTTPException(status_code=409, detail="Issue title already exists in this project")
        i.title = payload.title
    if payload.desc is not None:
        i.desc = payload.desc
    if payload.status is not None:
        i.status = payload.status
    if payload.priority is not None:
        i.priority = payload.priority
    if payload.assignee_id is not None:
        i.assignee_id = payload.assignee_id
    db.add(i); db.commit(); db.refresh(i)
    return i

@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: int, db: Annotated[Session, Depends(get_db)],
                 me: Annotated[User, Depends(get_current_user)]):
    i = db.get(Issue, issue_id)
    if not i:
        raise HTTPException(status_code=404, detail="Issue not found")
    if i.reporter_id != me.id:
        raise HTTPException(status_code=403, detail="Now allowed")
    db.delete(i)
    db.commit()
    return