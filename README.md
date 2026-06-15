# TP CI/CD — API de tâches (Flask)

[![CI](https://github.com/coachprotalent/tp-cicd-flask/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/coachprotalent/tp-cicd-flask/actions/workflows/ci.yml)
[![CD](https://github.com/coachprotalent/tp-cicd-flask/actions/workflows/cd.yml/badge.svg?branch=main)](https://github.com/coachprotalent/tp-cicd-flask/actions/workflows/cd.yml)

Application support des TP CI/CD & DevSecOps.

- 📘 [TP 1 — CI/CD & DevSecOps](./TP-CICD-DevSecOps.md)
- 📗 [TP 2 — Travail collaboratif sur un dépôt GitHub](./TP2-Travail-Collaboratif-GitHub.md)

## Structure

```
.
├── app/
│   ├── __init__.py
│   └── main.py            # l'application Flask
├── tests/
│   └── test_main.py       # les tests
├── requirements.txt       # dépendances de l'app
├── requirements-dev.txt   # dépendances de dev (tests, lint, sécurité…)
├── Dockerfile             # conteneurisation (multi-stage, non-root)
├── .dockerignore
├── pyproject.toml         # configuration de ruff
├── .github/
│   ├── workflows/ci.yml   # pipeline d'intégration continue
│   ├── workflows/cd.yml   # déploiement continu vers Azure
│   └── dependabot.yml
└── .gitignore
```

## Lancer en local

```bash
python -m venv .venv

# Activation - macOS / Linux
source .venv/bin/activate
# Activation - Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt -r requirements-dev.txt
flask --app app.main run
```

Ouvrez http://127.0.0.1:5000/health → `{"status":"ok"}`

> Port : **5000** en local via Flask (dev) ; **8000** via Docker/Azure (gunicorn).

## Tester

```bash
pytest -v
pytest --cov=app --cov-report=term-missing
```

## Auteur

- (votre prénom ici)
