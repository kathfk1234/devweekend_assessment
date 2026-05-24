"""Routes for HTML page rendering."""
from fastapi import APIRouter, Depends, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from jinja2 import TemplateNotFound
from datetime import datetime
from app.database import get_db
from app import crud, schemas
from app.services.search import search_notes as search_notes_service

router = APIRouter(tags=["pages"])


@router.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    """Home page showing dashboard overview."""
    # Get statistics
    all_clients = crud.get_all_clients(db)
    all_notes = crud.get_all_session_notes(db, skip=0, limit=10)
    follow_up_notes = crud.get_follow_up_required_notes(db)
    
    return await request.app.state.templates.TemplateResponse("index.html", {
        "request": request,
        "clients_count": len(all_clients),
        "notes_count": len(all_notes),
        "follow_up_count": len(follow_up_notes),
        "recent_notes": all_notes[:5]
    })


@router.get("/clients", response_class=HTMLResponse)
async def clients_page(request: Request, db: Session = Depends(get_db)):
    """Clients list page."""
    clients = crud.get_all_clients(db)
    return await request.app.state.templates.TemplateResponse("clients.html", {
        "request": request,
        "clients": clients
    })


@router.get("/clients/new", response_class=HTMLResponse)
async def new_client_page(request: Request):
    """New client form page."""
    return await request.app.state.templates.TemplateResponse("client_form.html", {
        "request": request,
        "is_new": True
    })


@router.get("/clients/{client_id}", response_class=HTMLResponse)
async def client_detail_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    """Client detail page with notes."""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return await request.app.state.templates.TemplateResponse("client_detail.html", {
        "request": request,
        "client": client,
        "notes": client.notes
    })


@router.get("/clients/{client_id}/edit", response_class=HTMLResponse)
async def edit_client_page(request: Request, client_id: int, db: Session = Depends(get_db)):
    """Edit client form page."""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    return await request.app.state.templates.TemplateResponse("client_form.html", {
        "request": request,
        "is_new": False,
        "client": client
    })


@router.get("/notes", response_class=HTMLResponse)
async def notes_page(request: Request, db: Session = Depends(get_db)):
    """Session notes list page."""
    notes = crud.get_all_session_notes(db)
    tags = crud.get_all_tags(db)
    return await request.app.state.templates.TemplateResponse("notes.html", {
        "request": request,
        "notes": notes,
        "tags": tags
    })


@router.get("/notes/new", response_class=HTMLResponse)
async def new_note_page(request: Request, db: Session = Depends(get_db)):
    """New session note form page."""
    clients = crud.get_all_clients(db)
    tags = crud.get_all_tags(db)
    return await request.app.state.templates.TemplateResponse("note_form.html", {
        "request": request,
        "is_new": True,
        "clients": clients,
        "tags": tags
    })


@router.get("/notes/{note_id}", response_class=HTMLResponse)
async def note_detail_page(request: Request, note_id: int, db: Session = Depends(get_db)):
    """Session note detail page."""
    note = crud.get_session_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Session note not found")
    
    return await request.app.state.templates.TemplateResponse("note_detail.html", {
        "request": request,
        "note": note
    })


@router.get("/notes/{note_id}/edit", response_class=HTMLResponse)
async def edit_note_page(request: Request, note_id: int, db: Session = Depends(get_db)):
    """Edit session note form page."""
    note = crud.get_session_note(db, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Session note not found")
    
    clients = crud.get_all_clients(db)
    tags = crud.get_all_tags(db)
    
    return await request.app.state.templates.TemplateResponse("note_form.html", {
        "request": request,
        "is_new": False,
        "note": note,
        "clients": clients,
        "tags": tags
    })


@router.get("/search", response_class=HTMLResponse)
async def search_page(request: Request, q: str = "", db: Session = Depends(get_db)):
    """Search results page."""
    results = []
    if q:
        results = search_notes_service(db, q)
    
    return await request.app.state.templates.TemplateResponse("search.html", {
        "request": request,
        "query": q,
        "results": results
    })


@router.get("/follow-up", response_class=HTMLResponse)
async def follow_up_page(request: Request, db: Session = Depends(get_db)):
    """Follow-up reminders page."""
    notes = crud.get_follow_up_required_notes(db)
    return await request.app.state.templates.TemplateResponse("follow_up.html", {
        "request": request,
        "notes": notes
    })
