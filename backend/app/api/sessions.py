from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.db_models import Session, Message
from app.models.schemas import SessionCreate, SessionOut

router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.post("", response_model=SessionOut)
async def create_session(payload: SessionCreate, db: AsyncSession = Depends(get_db)):
    session = Session(title=payload.title.strip() or "New session")
    db.add(session)
    await db.commit()
    await db.refresh(session)

    stmt = (
        select(Session)
        .where(Session.id == session.id)
        .options(selectinload(Session.messages).selectinload(Message.artifacts))
    )
    result = await db.execute(stmt)
    session = result.scalar_one()

    return session


@router.get("/{session_id}", response_model=SessionOut)
async def get_session(session_id: UUID, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Session)
        .where(Session.id == session_id)
        .options(selectinload(Session.messages).selectinload(Message.artifacts))
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
