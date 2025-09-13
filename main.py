# main.py
import os
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import select
import aiofiles

from database import init_db, get_session
from models import Note

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Notes API with File Uploads")

# mount static files so uploaded files are served under /uploads/
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

# initialize DB
init_db()

@app.post("/notes", response_model=dict)
async def create_note(
        title: str = Form(...),
        content: str | None = Form(None),
        file: UploadFile | None = File(None),
):
    """
    Create a note. Optionally attach a file (image or PDF).
    - title: text form field
    - content: optional text form field
    - file: optional file upload
    """
    stored_filename = None
    original_filename = None
    content_type = None
    size = None

    if file:
        # Validate file content-type (simple allowlist)
        allowed = ["image/png", "image/jpeg", "image/jpg", "image/gif", "application/pdf"]
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        # create unique filename to avoid collisions
        ext = os.path.splitext(file.filename)[1]  # includes dot
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        original_filename = file.filename
        content_type = file.content_type

        file_path = os.path.join(UPLOAD_DIR, stored_filename)

        # stream file to disk asynchronously
        size = 0
        async with aiofiles.open(file_path, "wb") as out_file:
            while True:
                chunk = await file.read(1024 * 1024)  # read in 1MB chunks
                if not chunk:
                    break
                size += len(chunk)
                await out_file.write(chunk)

    # persist metadata to SQLite
    note = Note(
        title=title,
        content=content,
        filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        size=size,
    )

    with get_session() as session:
        session.add(note)
        session.commit()
        session.refresh(note)

    # return created note info (no binary data included)
    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "file_url": f"/uploads/{note.stored_filename}" if note.stored_filename else None,
        "filename": note.filename,
        "content_type": note.content_type,
        "size": note.size,
        "created_at": note.created_at.isoformat(),
    }

@app.get("/notes", response_model=list[dict])
def list_notes():
    with get_session() as session:
        notes = session.exec(select(Note).order_by(Note.created_at.desc())).all()

    results = []
    for n in notes:
        results.append({
            "id": n.id,
            "title": n.title,
            "content": n.content,
            "file_url": f"/uploads/{n.stored_filename}" if n.stored_filename else None,
            "filename": n.filename,
            "content_type": n.content_type,
            "size": n.size,
            "created_at": n.created_at.isoformat(),
        })
    return results

@app.get("/notes/{note_id}", response_model=dict)
def get_note(note_id: int):
    with get_session() as session:
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

    return {
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "file_url": f"/uploads/{note.stored_filename}" if note.stored_filename else None,
        "filename": note.filename,
        "content_type": note.content_type,
        "size": note.size,
        "created_at": note.created_at.isoformat(),
    }

@app.delete("/notes/{note_id}", response_model=dict)
def delete_note(note_id: int):
    with get_session() as session:
        note = session.get(Note, note_id)
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # remove associated file on disk if exists
        if note.stored_filename:
            path = os.path.join(UPLOAD_DIR, note.stored_filename)
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                # continue to delete DB record even if file delete fails
                print("Failed to remove file:", e)

        session.delete(note)
        session.commit()

    return {"detail": "Note deleted"}

# Simple HTML form to test in browser
@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <html>
      <head><title>Notes API - Upload</title></head>
      <body>
        <h3>Create a Note (with optional image/pdf)</h3>
        <form action="/notes" enctype="multipart/form-data" method="post">
          <label>Title: <input type="text" name="title" required/></label><br/><br/>
          <label>Content: <br/><textarea name="content" rows="6" cols="60"></textarea></label><br/><br/>
          <label>File: <input type="file" name="file" /></label><br/><br/>
          <button type="submit">Create Note</button>
        </form>

        <hr/>
        <h4>API docs</h4>
        <p>Open <a href="/docs">/docs</a> for automatic OpenAPI (Swagger) UI.</p>
      </body>
    </html>
    """
