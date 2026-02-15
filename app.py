from flask import Flask, render_template, redirect, request, make_response
import sqlite3
import uuid

app = Flask(__name__)
DB = "votes.db"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            image TEXT NOT NULL,
            votes INTEGER DEFAULT 0
        )
    """)

    c.execute("SELECT COUNT(*) FROM players")
    count = c.fetchone()[0]

    if count == 0:
        players = [
            ("A2D Nandha", "/static/a2d.jpg"),
            ("Madan Gowri", "/static/madangowri.jpg"),
            ("NRFM", "/static/nrfm.jpg"),
            ("Mr Kettavan", "/static/mrkettavan.jpg"),
            ("R Praggnanandhaa", "/static/praggnanandhaa.jpg"),
            ("Gukesh", "/static/gukesh.jpg"),
            ("Magnus Carlsen", "/static/magnus.jpg")
        ]

        for player in players:
            c.execute("INSERT INTO players (name, image) VALUES (?, ?)", player)

    conn.commit()
    conn.close()

init_db()

@app.route("/")
def home():
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Visitor table
    c.execute("""
        CREATE TABLE IF NOT EXISTS visitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT UNIQUE
        )
    """)

    device_id = request.cookies.get("device_id")

    if not device_id:
        device_id = str(uuid.uuid4())
        try:
            c.execute("INSERT INTO visitors (device) VALUES (?)", (device_id,))
            conn.commit()
        except:
            pass

    c.execute("SELECT COUNT(*) FROM visitors")
    visitor_count = c.fetchone()[0]

    c.execute("SELECT * FROM players ORDER BY votes DESC")
    players = c.fetchall()

    total_votes = sum(player[3] for player in players)

    conn.close()

    response = make_response(render_template(
        "index.html",
        players=players,
        visitors=visitor_count,
        total_votes=total_votes
    ))

    response.set_cookie("device_id", device_id)
    return response

@app.route("/vote/<int:player_id>")
def vote(player_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("UPDATE players SET votes = votes + 1 WHERE id = ?", (player_id,))
    conn.commit()
    conn.close()
    return redirect("/")
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))


