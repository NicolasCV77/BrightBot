# app.py
import os
import json
import re
import unicodedata
from collections import Counter
from flask import Flask, request, jsonify, render_template, redirect, url_for, session

app = Flask(__name__)
app.secret_key = "CAMBIA_ESTA_LLAVE_POR_ALGO_SEGURO"

# Paths
BASE_DIR = os.path.dirname(__file__)
USERS_PATH = os.path.join(BASE_DIR, "users.json")
FAQ_PATH = os.path.join(BASE_DIR, "faq.json")
SE_PATH = os.path.join(BASE_DIR, "systems_engineering.json")


# -------- UTILIDAD PARA CARGAR JSON --------
def load_json(path, fallback=None):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return fallback or []


# --------- CARGA BASE DE DATOS ---------
users = load_json(USERS_PATH, fallback=[
    {"email": "nicolas@u.com", "password": "1234", "name": "Nicolás"},
    {"email": "daniel@u.com", "password": "1234", "name": "Daniel"}
])

faq = load_json(FAQ_PATH)
se_faq = load_json(SE_PATH)


# ----------- NORMALIZACIÓN (sin tildes) -----------
def normalize(text):
    if not text:
        return ""
    s = text.lower()
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def tokenize(text):
    return re.findall(r"\w+", normalize(text))


# ----------- MATCHING CON minPalabras -----------

def find_best_match(query, knowledge):
    q_tokens = set(tokenize(query))
    q_word_count = len(q_tokens)

    best_idx = None
    best_score = 0

    for i, item in enumerate(knowledge):
        min_words = item.get("minPalabras", 1)

        # No cumple requisito de palabras -> ignorar
        if q_word_count < min_words:
            continue

        doc_tokens = set(tokenize(item["pregunta"] + " " + item["respuesta"]))
        score = len(q_tokens & doc_tokens)

        if score > best_score:
            best_idx = i
            best_score = score

    return best_idx, best_score


def get_top_matches(query, knowledge, n=3, exclude=None):
    q_tokens = set(tokenize(query))
    scores = []

    for i, item in enumerate(knowledge):
        if i == exclude:
            continue
        doc_tokens = set(tokenize(item["pregunta"] + " " + item["respuesta"]))
        score = len(q_tokens & doc_tokens)
        scores.append((score, i))  # Cambia aquí: guarda el índice en vez de la pregunta

    scores.sort(reverse=True)
    # Regresa los índices de los N mejores matches
    return [i for _, i in scores[:n]]

# ----------- HISTORIAL Y POPULARIDAD -----------
history_global = []
pop_counter = Counter()


# ----------- RUTAS HTML -----------

@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


@app.route("/login")
def login_get():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login_post():
    email = request.form.get("email", "").lower().strip()
    password = request.form.get("password", "").strip()

    user = next((u for u in users if u["email"] == email and u["password"] == password), None)

    if user:
        session["user"] = {
            "email": user["email"],
            "name": user.get("name", email.split("@")[0])
        }
        return redirect(url_for("dashboard"))

    return render_template("login.html", error="Usuario o contraseña incorrectos.")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))


@app.route("/dashboard")
def dashboard():
    if not session.get("user"):
        return redirect(url_for("login_get"))
    return render_template("dashboard.html", user=session.get("user"))


# ----------- API DEL CHAT -----------

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    pregunta = data.get("mensaje", "").strip()

    if not pregunta:
        return jsonify({"respuesta": "Escribe algo para poder ayudarte."})

    pregunta = normalize(pregunta)
    history_global.append(pregunta)
    pop_counter.update([pregunta])

    knowledge = (se_faq + faq) if session.get("user") else faq
    idx, score = find_best_match(pregunta, knowledge)

    if idx is not None and score > 0:
        respuesta = knowledge[idx]["respuesta"]
        if session.get("user"):
            nombre = session["user"]["name"]
            respuesta = f"{nombre}, {respuesta}"
        rec_indices = get_top_matches(pregunta, knowledge, exclude=idx)
        recommendations = [knowledge[i].get("preguntaOriginal", knowledge[i]["pregunta"]) for i in rec_indices]
        return jsonify({
            "found": True,
            "respuesta": respuesta,
            "recommendations": recommendations[:3]
        })

    rec_indices = get_top_matches(pregunta, knowledge)
    recommendations = [knowledge[i].get("preguntaOriginal", knowledge[i]["pregunta"]) for i in rec_indices]
    return jsonify({
        "found": False,
        "respuesta": "¿Quizás querías preguntar?",
        "recommendations": recommendations[:3]
    })


if __name__ == "__main__":
    app.run(debug=True)
