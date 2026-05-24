"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
from app.database import init_db
from app.routes import pages, clients, notes

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title="Therapy Notes Manager",
    description="A simple app to manage client therapy session notes with search and tagging",
    version="1.0.0"
)

# Setup templates
template_dir = os.path.join(os.path.dirname(__file__), "templates")
app.state.templates = Jinja2Templates(directory=template_dir)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Include routers
app.include_router(pages.router)
app.include_router(clients.router)
app.include_router(notes.router)


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
