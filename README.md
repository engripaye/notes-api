
# 📓 Notes API with File Uploads

A simple and professional **Notes API** built with **FastAPI + SQLite** that allows you to:

* Save text notes ✍️
* Attach files (Images/PDFs) 📂
* Retrieve, list, and delete notes
* Serve uploaded files as static content
---

This project demonstrates:

* File upload endpoints
* Handling binary data in Python
* Serving static files securely
* SQLite database integration with `sqlmodel`

---

## 🚀 Features

* Create notes with optional file attachments (images/PDFs).
* Store metadata (title, content, filename, size, MIME type, timestamp) in SQLite.
* Stream file uploads to disk using `aiofiles` (memory efficient).
* Serve uploaded files at `/uploads/{filename}`.
* Interactive API docs via **Swagger UI** at `/docs`.
* Simple HTML upload form at `/`.

---

## 🛠️ Tech Stack

* **Backend:** [FastAPI](https://fastapi.tiangolo.com/)
* **Database:** SQLite + SQLModel
* **Async File Handling:** aiofiles
* **Server:** Uvicorn

---

## 📂 Project Structure

```
notes-api/
├─ uploads/                 # Saved uploaded files (auto-created)
├─ notes.db                 # SQLite database (auto-created)
├─ main.py                  # FastAPI app with endpoints
├─ database.py              # Database engine/session
├─ models.py                # SQLModel definitions
├─ requirements.txt         # Dependencies
└─ README.md                # Documentation
```

---

## ⚡ Installation & Setup

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/notes-api.git
cd notes-api
```

### 2. Create Virtual Environment (Optional but recommended)

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the API

```bash
uvicorn main:app --reload
```

### 5. Access the API

* API Docs (Swagger): 👉 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
* HTML Form (manual test): 👉 [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📌 API Endpoints

### ➕ Create a Note

**POST** `/notes`

* Form Data: `title`, `content` (optional), `file` (optional)

Example:

```bash
curl -X POST "http://127.0.0.1:8000/notes" \
  -F "title=Meeting Notes" \
  -F "content=Discussed project roadmap" \
  -F "file=@/path/to/document.pdf;type=application/pdf"
```

---

### 📋 List Notes

**GET** `/notes`

```bash
curl http://127.0.0.1:8000/notes
```

---

### 🔎 Get a Single Note

**GET** `/notes/{note_id}`

```bash
curl http://127.0.0.1:8000/notes/1
```

---

### ❌ Delete a Note

**DELETE** `/notes/{note_id}`

```bash
curl -X DELETE http://127.0.0.1:8000/notes/1
```

---

### 📂 Access Uploaded Files

Files are served at:

```
/uploads/{stored_filename}
```

Example:

```
http://127.0.0.1:8000/uploads/8a3f2b123abc.pdf
```

---

## 📸 Screenshots

### Swagger UI

![Swagger UI](https://fastapi.tiangolo.com/img/index/index-03-swagger-ui-simple.png)

### HTML Upload Form

> Accessible at `/` for quick testing.

---

## 🔐 Security Considerations

* Allowed file types: **PNG, JPG, GIF, PDF**.
* Unique filenames generated to prevent conflicts.
* SQLite is used for simplicity (consider PostgreSQL for production).
* Authentication (JWT/OAuth2) can be added for real-world use.

---

## 🌟 Future Improvements

* Add **user authentication** (JWT or OAuth2).
* File size restrictions and virus scanning.
* Image preview and PDF inline rendering.
* Switch to PostgreSQL/MySQL for production environments.
* Add Docker support for easy deployment.

---

## 👨‍💻 Author

Developed with ❤️ using **FastAPI** and **SQLite**.

If you find this useful, don’t forget to ⭐ the repo!

---
