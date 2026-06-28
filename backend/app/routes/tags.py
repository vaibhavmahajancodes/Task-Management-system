from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth.permissions import get_current_user
from app.database.db import get_db
from app.models.tag import Tag
from app.models.user import User
from app.schemas.common import Message
from app.schemas.tag import TagCreate, TagOut

router = APIRouter(prefix="/tags", tags=["Tags"])

# Constants
_DEFAULT_LIMIT  = 50
_MAX_LIMIT      = 200
_MAX_SEARCH_LEN = 100

@router.get("", response_model=List[TagOut])
def list_tags(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Tag).order_by(Tag.name).all()


@router.post("", response_model=TagOut, status_code=201)
def create_tag(payload: TagCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    existing = db.query(Tag).filter(Tag.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="A tag with this name already exists.")
    tag = Tag(name=payload.name, color=payload.color)
    db.add(tag)
    db.commit()
    db.refresh(tag)
    return tag


@router.delete("/{tag_id}", response_model=Message)
def delete_tag(tag_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found.")
    db.delete(tag)
    db.commit()
    return Message(message=f"Tag '{tag.name}' deleted.")
