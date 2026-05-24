"""Routes for client management."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app import crud, schemas
from app.services.search import search_clients

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=schemas.ClientResponse)
def create_client(client: schemas.ClientCreate, db: Session = Depends(get_db)):
    """Create a new client."""
    return crud.create_client(db, client)


@router.get("/", response_model=list[schemas.ClientResponse])
def list_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """List all clients with pagination."""
    return crud.get_all_clients(db, skip=skip, limit=limit)


@router.get("/search", response_model=list[schemas.ClientResponse])
def search_client_endpoint(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """Search clients by name or contact info."""
    results = search_clients(db, q)
    if not results:
        return []
    return results


@router.get("/{client_id}", response_model=schemas.ClientWithNotes)
def get_client(client_id: int, db: Session = Depends(get_db)):
    """Get a specific client with their session notes."""
    client = crud.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=schemas.ClientResponse)
def update_client(client_id: int, client_update: schemas.ClientUpdate, db: Session = Depends(get_db)):
    """Update a client's information."""
    client = crud.update_client(db, client_id, client_update)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.delete("/{client_id}")
def delete_client(client_id: int, db: Session = Depends(get_db)):
    """Delete a client and all associated notes."""
    success = crud.delete_client(db, client_id)
    if not success:
        raise HTTPException(status_code=404, detail="Client not found")
    return {"message": "Client deleted successfully"}
