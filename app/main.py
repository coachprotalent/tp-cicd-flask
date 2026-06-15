"""Petite API de gestion de tâches (Flask) pour le TP CI/CD."""
from flask import Flask, jsonify, request

app = Flask(__name__)

# Base de données "en mémoire" pour simplifier le TP
_tasks = [
    {"id": 1, "title": "Apprendre la CI/CD", "done": False},
    {"id": 2, "title": "Forker le projet", "done": True},
]


@app.get("/")
def index():
    return jsonify({"message": "Bienvenue sur l'API du TP CI/CD !"})


@app.get("/health")
def health():
    """Route de santé : utilisée par Azure et les tests pour vérifier que l'app tourne."""
    return jsonify({"status": "ok"})


@app.get("/api/tasks")
def list_tasks():
    return jsonify(_tasks)


@app.get("/api/tasks/<int:task_id>")
def get_task(task_id):
    task = next((t for t in _tasks if t["id"] == task_id), None)
    if task is None:
        return jsonify({"error": "tâche introuvable"}), 404
    return jsonify(task)


@app.post("/api/tasks")
def create_task():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "le champ 'title' est requis"}), 400
    new_id = max((t["id"] for t in _tasks), default=0) + 1
    task = {"id": new_id, "title": title, "done": False}
    _tasks.append(task)
    return jsonify(task), 201


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
