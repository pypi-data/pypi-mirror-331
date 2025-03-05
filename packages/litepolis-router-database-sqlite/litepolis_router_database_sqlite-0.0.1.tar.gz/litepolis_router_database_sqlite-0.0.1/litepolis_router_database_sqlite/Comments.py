from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, select

from .utils import *

# Define the Conversation model
class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    comment: str
    user_id: int
    conversation_id: int
    moderated: bool = False
    approved: bool = False
    # random: bool = False # Remove random, implement later if needed


router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/", response_model=Comment, status_code=201)
def create_comment(comment: Comment, session: Session = Depends(get_session)):
    session.add(comment)
    session.commit()
    session.refresh(comment)
    return comment


@router.get("/", response_model=List[Comment])
def read_comments(session: Session = Depends(get_session)):
    comments = session.exec(select(Comment)).all()
    return comments


@router.get("/{comment_id}", response_model=Comment)
def read_comment(comment_id: int, session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    return comment


@router.patch("/{comment_id}", response_model=Comment)
def update_comment(comment_id: int, comment: Comment, session: Session = Depends(get_session)):
    db_comment = session.get(Comment, comment_id)
    if not db_comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    comment_data = comment.model_dump(exclude_unset=True)
    for key, value in comment_data.items():
        setattr(db_comment, key, value)

    session.add(db_comment)
    session.commit()
    session.refresh(db_comment)
    return db_comment


@router.delete("/{comment_id}")
def delete_comment(comment_id: int, session: Session = Depends(get_session)):
    comment = session.get(Comment, comment_id)
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    session.delete(comment)
    session.commit()
    return {"ok": True}

create_db_and_tables()
