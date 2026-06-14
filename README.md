# 📝 Quick Note Application

A lightweight, full-stack note-taking web application built with **Python (Flask)** and **SQLite**. Users can register an account, log in securely, write and save personal notes, and delete them — all from a single page with no reloads. Each user's notes are completely private and isolated from other accounts.

> 🚀 **Live Demo:** [https://quick-note-application.onrender.com](https://quick-note-application-1-q5lc.onrender.com)

---

## ✨ Features

- 🔐 **User Authentication** — Register and log in with a username and password. Passwords are securely hashed using Werkzeug — never stored in plain text.
- 🗒️ **Per-user Notes** — Every note is tied to the logged-in user. You only ever see your own notes.
- ⚡ **No Page Reloads** — Notes are saved and displayed using JavaScript `fetch` API calls in the background.
- 🗑️ **Delete Notes** — Remove any note instantly with a single click.
- 🕒 **Timestamps** — Every note shows the exact date and time it was saved.
- 💾 **Persistent Storage** — Notes and user accounts are stored in a local SQLite database, so data survives server restarts.
- 📱 **Responsive Design** — Works on desktop and mobile screens.
- 🎨 **Notebook Aesthetic** — Styled with a handcrafted paper/index-card look using lined background, washi-tape accents, and serif typography.

---

## 🗂️ Project Layout

```
Quick-Note-Application/
│
├── app.py                  # Flask application — routes, auth, API, DB setup
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
│
├── static/
│   └── style.css           # Shared stylesheet for all pages
│
└── templates/
    ├── login.html          # Sign-in page
    ├── register.html       # Sign-up / account creation page
    └── index.html          # Main notebook page (protected)
```

> **Note:** `notes.db` (the SQLite database) is created automatically the first time you run the app. It is excluded from version control via `.gitignore`.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3, Flask |
| Database | SQLite (via Python's built-in `sqlite3`) |
| Auth | Werkzeug password hashing, Flask sessions |
| Frontend | HTML5, CSS3, Vanilla JavaScript (Fetch API) |
| Fonts | Google Fonts — IBM Plex Mono, Lora |
| Deployment | Render (gunicorn) |

---

## 🔄 Request / Response Flow

```
Browser                        Flask Server                    SQLite DB
   |                               |                               |
   |-- POST /api/register -------> |                               |
   |   { username, password }      |-- INSERT INTO users --------> |
   |<-- 201 { username } --------- |<-- user_id ------------------ |
   |                               |                               |
   |-- POST /api/login ----------> |                               |
   |   { username, password }      |-- SELECT user, verify hash -> |
   |<-- 200 { username } --------- |   set session cookie          |
   |                               |                               |
   |-- POST /api/notes ----------> |                               |
   |   { content }                 |-- INSERT INTO notes --------> |
   |<-- 201 { id, content, time }  |<-- new note ------------------ |
   |                               |                               |
   |-- GET /api/notes -----------> |                               |
   |                               |-- SELECT WHERE user_id -----> |
   |<-- 200 [ ...notes ] --------- |<-- rows ------------------- - |
   |                               |                               |
   |-- DELETE /api/notes/:id ----> |                               |
   |                               |-- DELETE WHERE id+user_id --> |
   |<-- 200 { deleted: id } ------ |                               |
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.7 or higher
- pip

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/srirambehera035/Quick-Note-Application.git
cd Quick-Note-Application
```

**2. Install dependencies**
```bash
pip install -r requirements.txt
```

**3. Run the app**
```bash
python app.py
```

**4. Open in browser**
```
http://127.0.0.1:5000
```

You will be redirected to the login page. Click **"Create one"** to register a new account, then sign in and start writing notes.

> The SQLite database (`notes.db`) is created automatically on first run — no setup needed.

---

## 🔌 API Reference

All API endpoints return JSON.

### Auth

| Method | Endpoint | Description | Body |
|---|---|---|---|
| `POST` | `/api/register` | Create a new account | `{ username, password }` |
| `POST` | `/api/login` | Sign in | `{ username, password }` |
| `POST` | `/api/logout` | Sign out | — |

### Notes (requires login)

| Method | Endpoint | Description | Body |
|---|---|---|---|
| `GET` | `/api/notes` | Get all notes for current user | — |
| `POST` | `/api/notes` | Create a new note | `{ content }` |
| `DELETE` | `/api/notes/<id>` | Delete a note by ID | — |

### Example responses

**POST /api/notes** → `201 Created`
```json
{
  "id": 5,
  "content": "Buy milk and eggs",
  "created_at": "2026-06-14T10:32:11Z"
}
```

**GET /api/notes** → `200 OK`
```json
[
  { "id": 5, "content": "Buy milk and eggs", "created_at": "2026-06-14T10:32:11Z" },
  { "id": 4, "content": "Read chapter 3", "created_at": "2026-06-13T18:14:05Z" }
]
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE users (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    username     TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at   TEXT NOT NULL
);

CREATE TABLE notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL,
    content    TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
```

---

## 🔒 Security Notes

- Passwords are hashed with **Werkzeug's `generate_password_hash`** (PBKDF2-SHA256) before storage — plain text passwords are never saved.
- Sessions are signed with a **secret key** stored server-side. Change the default key before deploying publicly:
  ```bash
  export SECRET_KEY="your-long-random-secret-here"
  ```
- Notes are always filtered by `user_id` from the session — users cannot access or delete another user's notes.
- Deleting a note checks both `id` AND `user_id`, preventing unauthorized deletion.

---

## 📦 Deployment (Render)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → New Web Service → connect your repo
3. Set **Start Command** to:
   ```
   gunicorn app:app
   ```
4. Set the `SECRET_KEY` environment variable in Render's dashboard
5. Deploy — Render gives you a public URL automatically

> Free tier apps on Render spin down after inactivity. The first request after a period of inactivity may take ~30 seconds to wake up.

---

## 🤝 Contributing

Contributions are welcome! Feel free to open an issue or submit a pull request.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m "Add your feature"`
4. Push to the branch: `git push origin feature/your-feature`
5. Open a Pull Request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 👤 Author

**Sriram Behera**
- GitHub: [@srirambehera035](https://github.com/srirambehera035)

---

<p align="center">Made with ☕ and Flask</p>

```
