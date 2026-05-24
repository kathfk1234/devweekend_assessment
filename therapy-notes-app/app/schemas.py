"""Pydantic schemas for validation and serialization."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class TagBase(BaseModel):
    """Base schema for tags."""
    name: str = Field(..., min_length=1, max_length=100)


class TagCreate(TagBase):
    """Schema for creating a tag."""
    pass


class TagResponse(TagBase):
    """Schema for returning tag data."""
    id: int

    class Config:
        from_attributes = True


class ClientBase(BaseModel):
    """Base schema for clients."""
    full_name: str = Field(..., min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    contact_info: Optional[str] = Field(None, max_length=255)


class ClientCreate(ClientBase):
    """Schema for creating a client."""
    pass


class ClientUpdate(BaseModel):
    """Schema for updating a client."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=255)
    age: Optional[int] = Field(None, ge=0, le=150)
    contact_info: Optional[str] = Field(None, max_length=255)


class ClientResponse(ClientBase):
    """Schema for returning client data."""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ClientWithNotes(ClientResponse):
    """Schema for returning client data with notes."""
    notes: List['SessionNoteResponse'] = []

    class Config:
        from_attributes = True


class SessionNoteBase(BaseModel):
    """Base schema for session notes."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    session_date: datetime
    follow_up_required: bool = False


class SessionNoteCreate(SessionNoteBase):
    """Schema for creating a session note."""
    client_id: int
    tag_ids: List[int] = []


class SessionNoteUpdate(BaseModel):
    """Schema for updating a session note."""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    session_date: Optional[datetime] = None
    follow_up_required: Optional[bool] = None
    tag_ids: Optional[List[int]] = None


class SessionNoteResponse(SessionNoteBase):
    """Schema for returning session note data."""
    id: int
    client_id: int
    created_at: datetime
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


class SessionNoteWithClient(SessionNoteResponse):
    """Schema for returning session note with client data."""
    client: ClientResponse

    class Config:
        from_attributes = True


# Update forward references
ClientWithNotes.model_rebuild()
