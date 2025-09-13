# main.py
import os, uuid, aiofiles
from fastapi import FastAPI, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select
from fastapi.middleware.cors import CORSMiddleware
from database import init_db, get_session
from models import User, Note
from auth import hash_password, verify_password, create_access_token, get_current_user

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Notes API with Users & File Uploads")
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://127.0.0.1:5500"] for frontend only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------- User Routes ----------------
@app.post("/register")
def register(username: str = Form(...), password: str = Form(...)):
    with get_session() as session:
        existing = session.exec(select(User).where(User.username == username)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        user = User(username=username, password_hash=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
        return {"id": user.id, "username": user.username}


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    with get_session() as session:
        user = session.exec(select(User).where(User.username == form_data.username)).first()
        if not user or not verify_password(form_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        token = create_access_token({"sub": user.username})
        return {"access_token": token, "token_type": "bearer"}


# ---------------- Notes Routes ----------------
@app.post("/notes")
async def create_note(
        title: str = Form(...),
        content: str | None = Form(None),
        file: UploadFile | None = File(None),
        current_user: User = Depends(get_current_user),
):
    stored_filename, original_filename, content_type, size = None, None, None, None

    if file:
        allowed = ["image/png", "image/jpeg", "image/jpg", "image/gif", "application/pdf"]
        if file.content_type not in allowed:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

        ext = os.path.splitext(file.filename)[1]
        stored_filename = f"{uuid.uuid4().hex}{ext}"
        original_filename = file.filename
        content_type = file.content_type
        size = 0

        async with aiofiles.open(os.path.join(UPLOAD_DIR, stored_filename), "wb") as out_file:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                await out_file.write(chunk)

    note = Note(
        title=title,
        content=content,
        filename=original_filename,
        stored_filename=stored_filename,
        content_type=content_type,
        size=size,
        owner_id=current_user.id,
    )
    with get_session() as session:
        session.add(note)
        session.commit()
        session.refresh(note)

    return {"id": note.id, "title": note.title,
            "file_url": f"/uploads/{note.stored_filename}" if note.stored_filename else None}


@app.get("/notes")
def list_notes(current_user: User = Depends(get_current_user)):
    with get_session() as session:
        notes = session.exec(select(Note).where(Note.owner_id == current_user.id)).all()
    return [{"id": n.id, "title": n.title, "content": n.content,
             "file_url": f"/uploads/{n.stored_filename}" if n.stored_filename else None} for n in notes]


@app.delete("/notes/{note_id}")
def delete_note(note_id: int, current_user: User = Depends(get_current_user)):
    with get_session() as session:
        note = session.get(Note, note_id)
        if not note or note.owner_id != current_user.id:
            raise HTTPException(status_code=404, detail="Note not found or not yours")

        if note.stored_filename:
            path = os.path.join(UPLOAD_DIR, note.stored_filename)
            if os.path.exists(path):
                os.remove(path)

        session.delete(note)
        session.commit()
    return {"detail": "Note deleted"}


# Simple HTML homepage for testing
@app.get("/", response_class=HTMLResponse)
def homepage():
    return """
    <h2>Notes API with Authentication</h2>
    <p>Use <a href='/docs'>/docs</a> to test registration, login, and note APIs.</p>
    """
