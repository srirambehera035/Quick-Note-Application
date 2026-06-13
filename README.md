# Quick Note

A single-page notes app with user accounts: a Flask backend stores users and notes in a SQLite database, and the page fetches/saves notes via a small JSON API. Each person's notes are private to their account.

## Run it

```bash
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000 — you'll be sent to **/login**. Click "Create one" to register a new account (username 3+ chars, password 6+ chars), then sign in.

## Project layout

```
quicknote/
├── app.py                 # Flask app + SQLite models
├── requirements.txt
├── static/
│   └── style.css          # shared stylesheet for all pages
└── templates/
    ├── login.html
    ├── register.html
    └── index.html          # the notebook
```

## How it works

- `app.py` — Flask server with:
  - `GET /login`, `GET /register` — the sign-in and sign-up pages
  - `POST /api/register`, `POST /api/login`, `POST /api/logout` — account creation, session login, and logout
  - `GET /api/notes`, `POST /api/notes`, `DELETE /api/notes/<id>` — notes scoped to the signed-in user
  - `GET /` — the notebook page (redirects to `/login` if not signed in)
  - On first run it creates `notes.db` (SQLite) with `users` and `notes` tables. Passwords are hashed with Werkzeug's `generate_password_hash`.
- `static/style.css` — one shared stylesheet (index-card / notepad look) used by all three pages via `{{ url_for('static', filename='style.css') }}`.
- `templates/login.html` / `templates/register.html` — matching sign-in / sign-up cards.
- `templates/index.html` — the notebook: a textarea + "Save note" button, plus your username and a "Sign out" button. JavaScript `fetch` calls hit the API above and re-render the note list — no page reloads.

## Request/response flow

1. **Sign up or sign in** — the form posts JSON to `/api/register` or `/api/login`. The server checks/creates the account and stores `user_id` in a signed session cookie.
2. **Write a note** — click **Save note** (or Cmd/Ctrl+Enter). The page sends `POST /api/notes` with `{"content": "..."}`.
3. The server checks the session, validates the content, and inserts a row into SQLite tagged with your `user_id`.
4. The page re-fetches `GET /api/notes`, which returns only *your* notes, and redraws the list — notes persist across reloads and are kept separate per account.
5. **Sign out** clears the session and sends you back to `/login`.

## Notes on the secret key

`app.secret_key` falls back to a dev value. For anything beyond local testing, set a real secret via an environment variable:

```bash
export SECRET_KEY="some-long-random-string"
```
