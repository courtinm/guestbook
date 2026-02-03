import psycopg2
from psycopg2.extras import RealDictCursor
from flask import redirect, url_for
from flask import Flask, request, jsonify, render_template

import redis
import os
app = Flask(__name__)

redis_host = os.getenv("REDIS_HOST", "localhost")
r = redis.Redis(host=redis_host, port=6379, db=0)

pg_host = os.environ["POSTGRES_HOST"]
db_user = os.environ["POSTGRES_USER"]
db_password = os.environ["POSTGRES_PASSWORD"]
bd_name = os.environ["POSTGRES_DB"]

def get_pg_connection():
    return psycopg2.connect(
        host=pg_host,
        user=db_user,
        password=db_password,
        dbname=bd_name,
        cursor_factory=RealDictCursor 
    )

@app.route("/", methods=["GET", "POST"])
def home():
    count = r.incr("page_count")

    conn = get_pg_connection()
    cur = conn.cursor()

    if request.method == "POST":
        author = request.form.get("author")
        content = request.form.get("content")

        if author and content:
            cur.execute(
                "INSERT INTO messages (author, content) VALUES (%s, %s)",
                (author, content)
            )
            conn.commit()

        cur.close()
        conn.close()

        # 🔹 Redirection après POST
        return redirect(url_for("home"))

    cur.execute("SELECT * FROM messages ORDER BY created_at DESC")
    messages = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("index.html", count=count, messages=messages)


@app.route("/api/reset")
def reset():
    r.delete("page_count")
    return "Compteur remis à zéro !"

@app.route("/api/messages", methods=["GET"])
def get_messages():
    conn = get_pg_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM messages ORDER BY created_at DESC")
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(messages)


@app.route("/api/messages", methods=["POST"])
def add_message():
    data = request.get_json()
    author = data.get("author")
    content = data.get("content")

    if not author or not content:
        return jsonify({"error": "author and content required"}), 400

    conn = get_pg_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO messages (author, content) VALUES (%s, %s) RETURNING *",
        (author, content)
    )
    new_message = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    return jsonify(new_message), 201

if __name__ == "__main__":
    app.run(port=8000, debug=True, host="0.0.0.0")
