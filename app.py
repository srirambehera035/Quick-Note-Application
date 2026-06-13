from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "notes.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
    )
    conn.commit()
    conn.close()


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Not logged in."}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


# ---------- Pages ----------

@app.route("/")
@login_required
def index():
    return render_template("index.html", username=session.get("username"))


@app.route("/login", methods=["GET"])
def login():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("login.html")


@app.route("/register", methods=["GET"])
def register():
    if "user_id" in session:
        return redirect(url_for("index"))
    return render_template("register.html")


# ---------- Auth API ----------

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    if len(username) < 3:
        return jsonify({"error": "Username must be at least 3 characters."}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    conn = get_db()
    existing = conn.execute(
        "SELECT id FROM users WHERE username = ?", (username,)
    ).fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "That username is already taken."}), 409

    password_hash = generate_password_hash(password)
    created_at = datetime.utcnow().isoformat() + "Z"
    cursor = conn.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, created_at),
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()

    session["user_id"] = user_id
    session["username"] = username
    return jsonify({"username": username}), 201


@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    conn = get_db()
    user = conn.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?",
        (username,),
    ).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect username or password."}), 401

    session["user_id"] = user["id"]
    session["username"] = user["username"]
    return jsonify({"username": user["username"]})


@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.clear()
    return jsonify({"ok": True})


# ---------- Notes API ----------

@app.route("/api/notes", methods=["GET"])
@login_required
def get_notes():
    conn = get_db()
    rows = conn.execute(
        "SELECT id, content, created_at FROM notes WHERE user_id = ? ORDER BY id DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()
    notes = [dict(row) for row in rows]
    return jsonify(notes)


@app.route("/api/notes", methods=["POST"])
@login_required
def create_note():
    data = request.get_json(silent=True) or {}
    content = (data.get("content") or "").strip()

    if not content:
        return jsonify({"error": "Note content cannot be empty."}), 400

    if len(content) > 2000:
        return jsonify({"error": "Note is too long (max 2000 characters)."}), 400

    created_at = datetime.utcnow().isoformat() + "Z"

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO notes (user_id, content, created_at) VALUES (?, ?, ?)",
        (session["user_id"], content, created_at),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": new_id, "content": content, "created_at": created_at}), 201


@app.route("/api/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    conn = get_db()
    cursor = conn.execute(
        "DELETE FROM notes WHERE id = ? AND user_id = ?",
        (note_id, session["user_id"]),
    )
    conn.commit()
    deleted = cursor.rowcount
    conn.close()

    if deleted == 0:
        return jsonify({"error": "Note not found."}), 404

    return jsonify({"deleted": note_id})


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
