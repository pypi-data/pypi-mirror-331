from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Field, Session, SQLModel, select

from .utils import *

# Define the Conversation model
class Conversation(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str
    creator_id: int
    # moderation: bool = False # Add moderation if needed


router = APIRouter(prefix="/conversations", tags=["conversations"])

@router.post("/", response_model=Conversation, status_code=201)
def create_conversation(conversation: Conversation, session: Session = Depends(get_session)):
    session.add(conversation)
    session.commit()
    session.refresh(conversation)
    return conversation


@router.get("/", response_model=List[Conversation])
def read_conversations(session: Session = Depends(get_session)):
    conversations = session.exec(select(Conversation)).all()
    return conversations


@router.get("/{conversation_id}", response_model=Conversation)
def read_conversation(conversation_id: int, session: Session = Depends(get_session)):
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conversation


@router.patch("/{conversation_id}", response_model=Conversation)
def update_conversation(conversation_id: int, conversation: Conversation, session: Session = Depends(get_session)):
    db_conversation = session.get(Conversation, conversation_id)
    if not db_conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation_data = conversation.model_dump(exclude_unset=True)
    for key, value in conversation_data.items():
        setattr(db_conversation, key, value)

    session.add(db_conversation)
    session.commit()
    session.refresh(db_conversation)
    return db_conversation


@router.delete("/{conversation_id}")
def delete_conversation(conversation_id: int, session: Session = Depends(get_session)):
    conversation = session.get(Conversation, conversation_id)
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    session.delete(conversation)
    session.commit()
    return {"ok": True}

create_db_and_tables()
