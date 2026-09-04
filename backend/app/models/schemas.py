from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict


class SessionCreate(BaseModel):
    title: str = Field(default="New session", max_length=200)


class ArtifactOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    artifact_type: str
    title: str
    content: str


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    role: str
    content: str
    sources: list = []
    created_at: datetime
    artifacts: list[ArtifactOut] = []


class SessionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[MessageOut] = []


class Source(BaseModel):
    episode: str
    guest: str
    timestamp: str | None = None
    score: float
    text: str


class ChatRequest(BaseModel):
    session_id: UUID
    message: str = Field(min_length=1, max_length=12000)
    mode: str = Field(default="default", pattern="^(default|ship30)$")
    provider: str | None = Field(default=None, pattern="^(ollama|anthropic|openai)$")
