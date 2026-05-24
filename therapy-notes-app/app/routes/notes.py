"""Routes for session notes management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services.search import search_notes, search_notes_by_tag, search_notes_by_multiple_tags

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("/", response_model=schemas.SessionNoteResponse)
def create_note(note: schemas.SessionNoteCreate, db: Session = Depends(get_db)):
    """Create a new session note."""
    # Verify client exists
    client = crud.get_client(db, note.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    try:
        return crud.create_session_note(db, note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=list[schemas.SessionNoteResponse])
def list_notes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all session notes with pagination."""
    return crud.get_all_session_notes(db, skip=skip, limit=limit)


@router.get("/search/text", response_model=list[schemas.SessionNoteResponse])
def search_notes_endpoint(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
    Search notes by title or content.
    Edge case: Search is case-insensitive and normalizes whitespace.
    """
    results = search_notes(db, q)
    if not results:
        return []
    return results


@router.get("/follow-up/all", response_model=list[schemas.SessionNoteResponse])
def get_follow_up_notes(db: Session = Depends(get_db)):
    """Get all notes that require follow-up."""
    return crud.get_follow_up_required_notes(db)


@router.get("/client/{client_id}", response_model=list[schemas.SessionNoteResponse])
def get_client_notes(client_id: int, db: Session = Depends(get_db)):
    """Get all notes for a specific client."""
    # Verify client exists
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return crud.get_notes_by_client(db, client_id)


@router.get("/{note_id}", response_model=schemas.SessionNoteWithClient)
def get_note(note_id: int, db: Session = Depends(get_db)):
    """Get a specific session note."""
    note = crud.get_session_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Session note not found")
    return note


@router.put("/{note_id}", response_model=schemas.SessionNoteResponse)
def update_note(note_id: int, note_update: schemas.SessionNoteUpdate, db: Session = Depends(get_db)):
    """Update a session note."""
    note = crud.get_session_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Session note not found")
    
    try:
        return crud.update_session_note(db, note_id, note_update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    """Delete a session note."""
    success = crud.delete_session_note(db, note_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session note not found")
    return {"message": "Session note deleted successfully"}
