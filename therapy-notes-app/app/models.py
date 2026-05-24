"""Database models for the Therapy Notes Manager."""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for many-to-many relationship between SessionNote and Tag
note_tags_association = Table(
    'note_tags_association',
    Base.metadata,
    Column('note_id', Integer, ForeignKey('session_notes.id', ondelete='CASCADE')),
    Column('tag_id', Integer, ForeignKey('tags.id', ondelete='CASCADE'))
)


class Client(Base):
    """Model representing a therapy client."""
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(255), index=True, nullable=False)
    age = Column(Integer, nullable=True)
    contact_info = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship
    notes = relationship("SessionNote", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Client(id={self.id}, full_name='{self.full_name}')>"


class SessionNote(Base):
    """Model representing a therapy session note."""
    __tablename__ = "session_notes"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey('clients.id', ondelete='CASCADE'), nullable=False, index=True)
    session_date = Column(DateTime, nullable=False, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    follow_up_required = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    client = relationship("Client", back_populates="notes")
    tags = relationship("Tag", secondary=note_tags_association, back_populates="notes")

    def __repr__(self):
        return f"<SessionNote(id={self.id}, client_id={self.client_id}, title='{self.title}')>"


class Tag(Base):
    """Model representing a tag for categorizing notes."""
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    
    # Relationship
    notes = relationship("SessionNote", secondary=note_tags_association, back_populates="tags")

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}')>"
