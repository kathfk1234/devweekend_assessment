"""Search service for notes and clients."""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app import models


def search_notes(db: Session, query: str, search_in_client: bool = False):
    """
    Search for session notes by title or content.
    
    Edge case: Search is case-insensitive and handles whitespace normalization.
    This allows searching for "panic attacks" to find "Panic Attacks" or "PANIC attacks".
    
    Args:
        db: Database session
        query: Search query string
        search_in_client: If True, also search in client names
    
    Returns:
        List of matching SessionNote objects
    """
    # Edge case: Normalize search query - strip whitespace and handle empty searches
    search_query = query.strip()
    if not search_query:
        return []
    
    # Create case-insensitive LIKE pattern
    search_pattern = f"%{search_query}%"
    
    # Build search conditions
    conditions = [
        models.SessionNote.title.ilike(search_pattern),
        models.SessionNote.content.ilike(search_pattern),
    ]
    
    # If search_in_client is True, also search client names
    if search_in_client:
        conditions.append(models.Client.full_name.ilike(search_pattern))
    
    # Execute query
    query_obj = db.query(models.SessionNote).filter(or_(*conditions))
    
    # If searching in client names, join the Client table
    if search_in_client:
        query_obj = query_obj.outerjoin(models.Client)
    
    return query_obj.order_by(models.SessionNote.session_date.desc()).all()


def search_notes_by_tag(db: Session, tag_id: int):
    """Search for notes that have a specific tag."""
    return db.query(models.SessionNote).join(
        models.SessionNote.tags
    ).filter(models.Tag.id == tag_id).order_by(
        models.SessionNote.session_date.desc()
    ).all()


def search_notes_by_multiple_tags(db: Session, tag_ids: list):
    """Search for notes that have any of the specified tags."""
    if not tag_ids:
        return []
    
    return db.query(models.SessionNote).join(
        models.SessionNote.tags
    ).filter(models.Tag.id.in_(tag_ids)).distinct().order_by(
        models.SessionNote.session_date.desc()
    ).all()


def search_clients(db: Session, query: str):
    """
    Search for clients by name or contact info.
    Case-insensitive with whitespace normalization.
    """
    search_query = query.strip()
    if not search_query:
        return []
    
    search_pattern = f"%{search_query}%"
    
    return db.query(models.Client).filter(
        or_(
            models.Client.full_name.ilike(search_pattern),
            models.Client.contact_info.ilike(search_pattern)
        )
    ).all()
