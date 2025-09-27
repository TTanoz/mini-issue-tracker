from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

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

@routerissuecomment.get("/{issue_id}/comments", response_model = list[CommentRead])
def list_comments(issue_id: int, db: Annotated[Session, Depends(get_db)],
) -> list[CommentRead]:
    if not db.get(Issue, issue_id):
        raise HTTPException(status_code=404, detail="Issue not found")
    comments = (db.query(Comment).filter(Comment.issue_id == issue_id).order_by(Comment.id.desc()).all())
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