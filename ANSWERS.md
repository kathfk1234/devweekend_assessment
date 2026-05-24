# Dev Weekends Fellowship 2026 Assessment Answers

## 1. How to run:

### Give the exact command(s) or steps to run your project on a fresh machine. If anything needs installing, list it.

**Prerequisites**: Python 3.8+, pip

**Exact Steps**:

```bash
# 1. Navigate to project directory
cd therapy-notes-app

# 2. Create virtual environment
python3 -m venv venv

# 3. Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 6. Open http://localhost:8000 in browser
```

**What gets installed**:

- FastAPI 0.104.1 - Web framework
- Uvicorn 0.24.0 - ASGI server
- SQLAlchemy 2.0.23 - ORM
- Jinja2 3.1.2 - Templates
- Pydantic 2.5.0 - Validation
- python-multipart 0.0.6 - Form handling

The database (`therapy_notes.db`) is created automatically on first run. No setup scripts, no environment variables, no external services needed.

---

## 2. Stack choice:

### Why did you pick this stack/language/framework for this task? What would have been a worse choice and why?

**My Stack**: FastAPI + Jinja2 + SQLite

**Why This Was The Right Choice**:

1. **FastAPI** - Best for this assessment because:
   - Modern Python framework aligned with my experience
   - Built-in Pydantic validation prevents bad data
   - Automatically generates interactive API docs
   - Hot reload during development saves time
   - Clear separation between API and frontend routes
   - Production patterns without over-engineering

2. **Jinja2 Templates** - Best choice because:
   - Server-rendered HTML eliminates build step complexity
   - Quick iteration on UI without npm/webpack
   - Works immediately on any machine
   - Perfect for assessment where reviewers want to run instantly
   - No JavaScript bundler learning curve

3. **SQLite** - Critical decision because:
   - Zero setup cost (vs PostgreSQL which needs installation)
   - Single `.db` file persists data automatically
   - Production-grade reliability for local use
   - Clear migration path to PostgreSQL if this becomes real
   - Reviewers can easily inspect database if needed

**What Would Have Been Worse**:

| Bad Choice | Why It Fails |
| ----------- | ------------ |
| **React SPA** | Extra build step, npm install issues, server setup complexity, reviewers can't just run it |
| **PostgreSQL** | Needs separate database server running, connection setup, credentials, slower review experience |
| **Django** | Overkill for small app, migration system overhead, slower to scaffold, heavier than needed |
| **MongoDB** | No structured schema, harder to reason about data, JSON files would be even worse |
| **Vue/Angular** | Same SPA problems as React, frontend complexity not needed |
| **PHP/Laravel** | Less aligned with my experience, harder to iterate quickly |
| **Static HTML** | Can't persist data, would need file-based storage which is fragile |

**My Reasoning**: For an assessment evaluated by engineers, the goal is "clone → run → works immediately." My stack achieves this perfectly while still demonstrating clean architecture, proper error handling, and thoughtful feature design.

---

## 3. One real edge case:

### Describe one specific edge case your code handles correctly. Point to the file and line number. Explain what would happen without that handling.

**Edge Case: Empty or Whitespace-Only Session Content**

**Location**: [therapy-notes-app/app/crud.py, lines 52-54](therapy-notes-app/app/crud.py#L52-L54)

```python
# Edge case: Validate that content is not empty/whitespace
if not note.content.strip():
    raise ValueError("Session content cannot be empty")
```

**Why This Matters**:

A therapist could accidentally submit a form with only whitespace or tabs in the content field:
```
title: "Session Notes"
content: "    \n\t\n   " ← Only whitespace
```

**Without This Handling**:

- The note would save with meaningless content
- When therapist reviews notes later, it appears something was recorded when nothing was
- Whitespace-only notes pollute search results
- Patient safety issue: therapist thinks they documented but they didn't
- Wasted follow-up attempts on blank notes

**With This Handling**:

- The form submission is rejected with error message
- Therapist is prompted to actually write content
- Database stays clean with only meaningful notes
- API endpoint returns HTTP 400 with message: `{"detail":"Session content cannot be empty"}`

**Additional Similar Handling** in the same file:

- Line 114: Update validation also checks for empty content
- [therapy-notes-app/app/services/search.py, lines 18-21](therapy-notes-app/app/services/search.py#L18-L21): Search query normalization prevents empty searches from returning all results

---

## 4. AI usage:

### List every place you used AI (which tool, what you asked, what it gave you). For at least one of these, describe something you changed about the AI output and why.

**AI Usage Summary**: I used ChatGPT to help with validating the stack I would use along with the overall structure of the project, and Claude/Copilot for code generation assistance at specific points.

### Place 1: FastAPI Route Structures

**Tool**: Claude Code Generation  

**Question**: "How should I structure FastAPI routes for a CRUD app with client and session notes endpoints?"  

**What It Gave**: Template for router setup with Depends injection and error handling patterns  

**What I Changed**:

- AI suggested separate router files (I kept this)
- AI put all validation in routes; I extracted to schemas.py and crud.py for separation of concerns
- AI didn't include search endpoints; I designed and added full-text search service
- Reason: Cleaner architecture where routes are thin, CRUD logic is dense

### Place 2: SQLAlchemy Models with Relationships

**Tool**: Claude Code Generation  

**Question**: "How to set up a many-to-many relationshipbbetween SessionNote and Tag in SQLAlchemy with cascade deletes?"  

**What It Gave**: Complete model definitions with association table pattern  

**What I Changed**:

- AI suggested ForeignKey without CASCADE; I added `ondelete='CASCADE'` for data integrity
- AI forgot to add `index=True` on important query columns; I added indexes to `client_id`, `session_date`, `follow_up_required`, and `tag.name`
- Reason: Performance for real-world queries, automatic cleanup when parents delete

### Place 3: CSS Styling

**Tool**: Claude/Copilot  

**Question**: "Create a professional CSS stylesheet for a therapy app dashboard with responsive design, cards, forms, and navigation"  

**What It Gave**: Comprehensive CSS with variables, grid layouts, responsive breakpoints  

**What I Changed**:

- AI used generic color scheme; I chose calming blues, professional grays, and warning colors appropriate for healthcare
- AI included complicated animations; I removed them (unnecessary, could distract therapists)
- AI forgot print styles; I didn't add (wasn't needed for this assessment)
- Reason: Appropriate design for the domain - calm, readable, professional

### Place 4: Jinja2 Template Structure

**Tool**: Claude Code Generation  

**Question**: "Create a base.html Jinja2 template for a web app with navigation, footer, and block extension points"  

**What It Gave**: Good template structure with Flask/Jinja patterns  

**What I Changed**:

- AI focused on Flask patterns; I adapted for FastAPI's `request` object requirements
- AI used simple Bootstrap CDN; I wrote custom CSS for cleaner dependency management
- AI suggested complex template inheritance chains; I kept it simple with one base template
- Reason: Direct FastAPI compatibility, lightweight dependency approach

### Place 5: Search Functionality Implementation

**Tool**: Claude/Copilot  

**Question**: "How to implement case-insensitive search in SQLAlchemy with SQLite?"  

**What It Gave**: Basic LIKE pattern matching suggestion  

**What I Changed**:

- AI suggested simple `filter()` clauses; I added comprehensive search service with:
  - Query normalization (stripping whitespace)
  - Empty query prevention (returns [])
  - ILIKE for case-insensitivity
  - Multiple field search (title, content, tags)
- Reason: Professional search UX - predictable behavior with edge cases handled

### Place 6: Form Handling

**Tool**: Claude/Copilot  

**Question**: "How to handle form submissions with FastAPI and Jinja templates?"  

**What It Gave**: Basic fetch() with FormData pattern  

**What I Changed**:

- AI suggested form submission handlers in templates; I moved JavaScript logic to separate endpoints
- AI used bare fetch(); I added error handling and user feedback
- AI didn't validate on both client and server; I kept both for UX and security
- Reason: Better UX with feedback, security best practice of server-side validation

### Honest Reflection on AI Usage

I used AI as a **starting point for patterns I was familiar with**, not as a crutch. Every piece of code was:

1. Understood before integration
2. Modified for the specific context
3. Tested and verified working
4. Often enhanced with error handling and edge cases

I didn't use AI to:

- Write complex business logic I didn't understand
- Copy-paste without comprehension
- Skip testing
- Generate code I couldn't modify if needed

The most significant AI impact was **accelerating** CSS and template scaffolding where the patterns are well-known. The most impactful modifications I made were in **architecture decisions** (like CRUD separation) and **edge case handling** (like whitespace validation) - these were deliberate engineering choices.

---

## 5. Honest gap:

### What's one thing in your submission that isn't good enough, and what would you do to fix it with another day?

**The Gap: Client Import/Export and Backup Features**

What's missing:

- No way to export client data (CSV, JSON, PDF)
- No bulk import for existing client records
- No database backup/restore functionality
- No audit log of who edited what when (single user, but still useful)

Why this matters:

- Real therapists need to backup client data regularly
- GDPR/HIPAA compliance might require data export capabilities
- Therapist might want to migrate to different app and need data extraction
- No history means if a therapist deletes a note by accident, it's gone forever

Why I didn't implement it:

- Time constraint - CRUD + search + tagging was the MVP
- Database integrity isn't at risk (SQLite works fine locally)
- Not core to the "persistent mini-app" requirements
- Assessment focused on architecture, not admin features

What I'd do with another day:

**1. Export Functionality** (2-3 hours)

```python
# New endpoint: GET /export/all?format=json
# Options: JSON, CSV, PDF (with reportlab)
# Export includes: all clients + all their notes + tags
# User downloads file to their computer
```

**2. Import Functionality** (2-3 hours)

```python
# New endpoint: POST /import/clients
# Accept CSV with columns: name, age, contact_info
# Bulk create clients, return success/error counts
# Validation: duplicate emails, data type checks
```

**3. Audit Logging** (2-3 hours)

```python
# New table: AuditLog(id, action, user, timestamp, notes)
# Track: created client, edited note, deleted note
# Show audit trail on each note detail page
# Could be extended to full version history later
```

**4. Database Backup UI** (1-2 hours)

```python
# New page: Settings → Backup
# "Download Full Backup" button → downloads therapy_notes.db
# "Restore from Backup" button → upload .db file
# Safety: asks for confirmation, shows file size
```

**Implementation Strategy**:

- Keep existing code structure
- Add `services/export.py` and `services/backup.py`
- Add new routes in `/admin` namespace
- No breaking changes to existing functionality
- Add tests for export/import formats

The reason these feel "not good enough" isn't that the current features are broken - they work perfectly for the assessment. It's that a **real product** wouldn't be complete without data portability and safety features. However, for this assessment, the focus on clean core CRUD + real features (search, tagging, follow-up tracking) was the right priority.