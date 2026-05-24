"""CRUD operations for database models."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app import models, schemas


# ==================== CLIENT OPERATIONS ====================

def create_client(db: Session, client: schemas.ClientCreate) -> models.Client:
    """Create a new client."""
    db_client = models.Client(
        full_name=client.full_name,
        age=client.age,
        contact_info=client.contact_info
    )
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def get_client(db: Session, client_id: int) -> models.Client:
    """Retrieve a client by ID."""
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def get_all_clients(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all clients with pagination."""
    return db.query(models.Client).offset(skip).limit(limit).all()


def update_client(db: Session, client_id: int, client_update: schemas.ClientUpdate) -> models.Client:
    """Update a client."""
    db_client = get_client(db, client_id)
    if not db_client:
        return None
    
    update_data = client_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_client, key, value)
    
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


def delete_client(db: Session, client_id: int) -> bool:
    """Delete a client and all associated notes."""
    db_client = get_client(db, client_id)
    if not db_client:
        return False
    
    db.delete(db_client)
    db.commit()
    return True


# ==================== SESSION NOTE OPERATIONS ====================

def create_session_note(db: Session, note: schemas.SessionNoteCreate) -> models.SessionNote:
    """Create a new session note with tags."""
    # Edge case: Validate that content is not empty/whitespace
    if not note.content.strip():
        raise ValueError("Session content cannot be empty")
    
    # Fetch tags
    tags = db.query(models.Tag).filter(models.Tag.id.in_(note.tag_ids)).all()
    
    db_note = models.SessionNote(
        client_id=note.client_id,
        session_date=note.session_date,
        title=note.title,
        content=note.content,
        follow_up_required=note.follow_up_required,
        tags=tags
    )
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def get_session_note(db: Session, note_id: int) -> models.SessionNote:
    """Retrieve a session note by ID."""
    return db.query(models.SessionNote).filter(models.SessionNote.id == note_id).first()


def get_notes_by_client(db: Session, client_id: int):
    """Retrieve all notes for a specific client."""
    return db.query(models.SessionNote).filter(
        models.SessionNote.client_id == client_id
    ).order_by(models.SessionNote.session_date.desc()).all()


def get_all_session_notes(db: Session, skip: int = 0, limit: int = 100):
    """Retrieve all session notes with pagination."""
    return db.query(models.SessionNote).offset(skip).limit(limit).order_by(
        models.SessionNote.session_date.desc()
    ).all()


def get_follow_up_required_notes(db: Session):
    """Retrieve all notes marked as requiring follow-up."""
    return db.query(models.SessionNote).filter(
        models.SessionNote.follow_up_required == True
    ).order_by(models.SessionNote.session_date.desc()).all()


def update_session_note(db: Session, note_id: int, note_update: schemas.SessionNoteUpdate) -> models.SessionNote:
    """Update a session note."""
    db_note = get_session_note(db, note_id)
    if not db_note:
        return None
    
    update_data = note_update.model_dump(exclude_unset=True)
    
    # Handle tags separately
    if 'tag_ids' in update_data:
        tag_ids = update_data.pop('tag_ids')
        tags = db.query(models.Tag).filter(models.Tag.id.in_(tag_ids)).all()
        db_note.tags = tags
    
    # Validate content if being updated
    if 'content' in update_data and not update_data['content'].strip():
        raise ValueError("Session content cannot be empty")
    
    for key, value in update_data.items():
        setattr(db_note, key, value)
    
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    return db_note


def delete_session_note(db: Session, note_id: int) -> bool:
    """Delete a session note."""
    db_note = get_session_note(db, note_id)
    if not db_note:
        return False
    
    db.delete(db_note)
    db.commit()
    return True


# ==================== TAG OPERATIONS ====================

def create_or_get_tag(db: Session, tag_name: str) -> models.Tag:
    """Create a new tag or retrieve existing one."""
    # Edge case: Normalize tag names for case-insensitive search
    normalized_name = tag_name.strip().lower()
    
    existing_tag = db.query(models.Tag).filter(
        models.Tag.name.ilike(normalized_name)
    ).first()
    
    if existing_tag:
        return existing_tag
    
    db_tag = models.Tag(name=normalized_name)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def get_all_tags(db: Session):
    """Retrieve all tags."""
    return db.query(models.Tag).all()


def get_tag(db: Session, tag_id: int) -> models.Tag:
    """Retrieve a tag by ID."""
    return db.query(models.Tag).filter(models.Tag.id == tag_id).first()


def get_or_create_tags(db: Session, tag_names: list) -> list:
    """Get or create multiple tags."""
    tags = []
    for tag_name in tag_names:
        tag = create_or_get_tag(db, tag_name)
        tags.append(tag)
    return tags


def delete_tag(db: Session, tag_id: int) -> bool:
    """Delete a tag."""
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False
    
    db.delete(db_tag)
    db.commit()
    return True
