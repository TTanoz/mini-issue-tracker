from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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

@routerprojectissue.get("/{project_id}/issues", response_model=list[IssueRead])
def list_project_issues(project_id: int,db: Annotated[Session, Depends(get_db)],
) -> list[IssueRead]:
    if not db.get(Project, project_id):
        raise HTTPException(status_code=404, detail="Project not found")
    issues = (
        db.query(Issue)
        .filter(Issue.project_id == project_id)
        .order_by(Issue.id.desc())
        .all()
    )
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