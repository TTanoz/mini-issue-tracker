from typing import Annotated, Literal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import asc, desc
from app.db.session import get_db
from app.models.user import User
from app.models.comment import Comment
from app.models.issue import Issue

from app.schemas.comment import CommentCreate, CommentRead
from app.deps import get_current_user

router = APIRouter(prefix="/comments", tags=["comments"])
routerissuecomment = APIRouter(prefix="/issues", tags=["issue_comments"])

@routerissuecomment.post("/{issue_id}/comments", response_model=CommentRead, status_code= status.HTTP_201_CREATED)
def create_comment(issue_id: int, payload: CommentCreate, db: Annotated[Session, Depends(get_db)],
                 me: Annotated[User, Depends(get_current_user)]):
    if not db.get(Issue, issue_id):
        raise HTTPException(status_code=404, detail="Issue not found")
    comment = Comment(content = payload.content, issue_id = issue_id, author_id = me.id)
    db.add(comment); db.commit(); db.refresh(comment)
    return comment

@routerissuecomment.get("/{issue_id}/comments", response_model = list[CommentRead],dependencies=[Depends(get_current_user)])
def list_comments(issue_id: int, db: Annotated[Session, Depends(get_db),],
                  skip: int = Query(0, ge=0),
                  limit: int = Query(50, ge=1, le=200),
                  q: str | None = Query(None, description="Filter by comment content (icontains)"),
                  sort_by: Literal["id", "content", "issue_id", "author_id", "created_at", "updated_at"] = "id",
                  sort_dir: Literal["asc", "desc"] = "asc"
) -> list[CommentRead]:
    if not db.get(Issue, issue_id):
        raise HTTPException(status_code=404, detail="Issue not found")
    query = db.query(Comment).filter(Comment.issue_id == issue_id)
    if q:
        query = query.filter(Comment.content.ilike(f"%{q}%"))
    col = getattr(Comment, sort_by)
    order = asc(col) if sort_dir == "asc" else desc(col)
    query = query.order_by(order)
    comments = query.offset(skip).limit(limit).all()
    return comments

@router.get("/{comment_id}", response_model = CommentRead)
def get_one_comment(comment_id: int, db: Annotated[Session, Depends(get_db)]):
    c = db.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    return c

@router.patch("/{comment_id}", response_model=CommentRead)
def patch_comment(comment_id: int, payload: CommentCreate, db: Annotated[Session, Depends(get_db)],
                me: Annotated[User, Depends(get_current_user)]):
    c = db.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != me.id:
        raise HTTPException(status_code=403, detail="Not allowed")
    c.content = payload.content
    db.add(c); db.commit(); db.refresh(c)
    return c

@router.delete("/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(comment_id: int, db: Annotated[Session, Depends(get_db)],
                 me: Annotated[User, Depends(get_current_user)]):
    c = db.get(Comment, comment_id)
    if not c:
        raise HTTPException(status_code=404, detail="Comment not found")
    if c.author_id != me.id:
        raise HTTPException(status_code=403, detail="Now allowed")
    db.delete(c)
    db.commit()
    return