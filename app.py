from flask import Flask, render_template, request, redirect, session
import sqlite3

from datetime import datetime
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Simple training data
texts = [
    "I feel very happy today",
    "I am sad and lonely",
    "I am feeling anxious",
    "I am very angry",
    "I feel calm and okay"
]

labels = ["happy", "sad", "anxious", "angry", "neutral"]

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)


app = Flask(__name__)
app.secret_key = "mindscribe_secret_key"



def get_db():
    return sqlite3.connect("journal.db")

@app.route("/", methods=["GET", "POST"])
def index():
    if "user_id" not in session:
        return redirect("/login")

    emotion = None
    if request.method == "POST":
        text = request.form["journal"]
        vec = vectorizer.transform([text])
        emotion = model.predict(vec)[0]

        db = get_db()
        db.execute(
            "INSERT INTO journal (entry, emotion, date, user_id) VALUES (?, ?, ?, ?)",
            (text, emotion, datetime.now(), session["user_id"])
        )
        db.commit()

    return render_template("index.html", emotion=emotion)


@app.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    response = ""
    if request.method == "POST":
        msg = request.form["message"].lower()

        if "sad" in msg or "lonely" in msg:
            response = "I'm really sorry you're feeling this way 💙 Writing things down can help. Would you like to try a small positive activity?"
        elif "anxious" in msg or "stress" in msg:
            response = "That sounds overwhelming. Try the 4-4-4 breathing technique: inhale 4s, hold 4s, exhale 4s."
        elif "angry" in msg:
            response = "It's okay to feel angry. Taking a pause before reacting can help regain balance."
        elif "happy" in msg:
            response = "That's wonderful 😊 What contributed to this feeling today?"
        else:
            response = "Thank you for opening up. Self-reflection is a strong step forward."


    return render_template("chatbot.html", response=response)

@app.route("/dashboard")
def dashboard():
    db = get_db()
    data = db.execute(
        "SELECT emotion, COUNT(*) FROM journal GROUP BY emotion"
    ).fetchall()
    return render_template("dashboard.html", data=data)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, password)
            )
            db.commit()
            return redirect("/login")
        except:
            return "User already exists"

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session["user_id"] = user[0]
            return redirect("/")
        else:
            return "Invalid credentials"

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


import os

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

