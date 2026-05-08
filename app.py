import os

import redis
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, jsonify, redirect, render_template, request, url_for

app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

pg_host = os.environ["POSTGRES_HOST"]
db_user = os.environ["POSTGRES_USER"]
db_password = os.environ["POSTGRES_PASSWORD"]
db_name = os.environ["POSTGRES_DB"]


def get_db_connection():
    return psycopg2.connect(
        host=pg_host,
        user=db_user,
        password=db_password,
        dbname=db_name,
        cursor_factory=RealDictCursor,
    )


@app.route("/ping")
def ping():
    return jsonify({"status": "ok"}), 200


@app.route("/health")
def health():
    try:
        r.ping()
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "detail": str(e)}), 503


@app.route("/", methods=["GET", "POST"])
def home():
    try:
        count = r.incr("page_count")
    except redis.RedisError:
        count = "N/A"

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        if request.method == "POST":
            author = request.form.get("author", "").strip()
            content = request.form.get("content", "").strip()
            if author and content:
                cur.execute(
                    "INSERT INTO messages (author, content) VALUES (%s, %s)",
                    (author, content),
                )
                conn.commit()
            return redirect(url_for("home"))

        cur.execute("SELECT * FROM messages ORDER BY created_at DESC")
        messages = cur.fetchall()
    finally:
        conn.close()

    return render_template("index.html", count=count, messages=messages)


@app.route("/api/reset")
def reset():
    r.delete("page_count")
    return jsonify({"message": "Visit counter reset."})


@app.route("/api/messages", methods=["GET"])
def get_messages():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM messages ORDER BY created_at DESC")
        messages = cur.fetchall()
    finally:
        conn.close()
    return jsonify(list(messages))


@app.route("/api/messages", methods=["POST"])
def add_message():
    data = request.get_json()
    if not data:
        return jsonify({"error": "JSON body required"}), 400
    author = data.get("author", "").strip()
    content = data.get("content", "").strip()
    if not author or not content:
        return jsonify({"error": "author and content are required"}), 400

    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO messages (author, content) VALUES (%s, %s) RETURNING *",
            (author, content),
        )
        new_message = cur.fetchone()
        conn.commit()
    finally:
        conn.close()
    return jsonify(dict(new_message)), 201


if __name__ == "__main__":
    app.run(port=8000, host="0.0.0.0")
