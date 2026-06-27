# TP CI/CD — API de tâches (Flask) · branche `starter`

> 🌿 Vous êtes sur la branche **`starter`** : le **squelette de départ** des TP.
> Il contient l'application Flask et ses tests, **mais pas** le pipeline CI/CD ni Docker : c'est vous qui allez les construire pas à pas.
> La **solution complète** (corrigé) se trouve sur la branche **`main`** du dépôt de référence.

## Par où commencer ?

- 📘 [TP 1 — CI/CD & DevSecOps](./TP-CICD-DevSecOps.md) — commencez ici
- 📗 [TP 2 — Travail collaboratif sur un dépôt GitHub](./TP2-Travail-Collaboratif-GitHub.md) — après le TP 1

## Structure (squelette)

```
.
├── app/
│   ├── __init__.py
│   └── main.py            # l'application Flask
├── tests/
│   └── test_main.py       # les tests de base
├── requirements.txt       # dépendances de l'app
├── requirements-dev.txt   # dépendances de dev (tests, lint, sécurité…)
├── pyproject.toml         # configuration de ruff
├── .gitignore
└── README.md
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

> Port : **5000** en local via Flask (dev) ; **8000** via Docker/Azure (gunicorn) une fois le TP avancé.

## Tester

```bash
pytest -v
pytest --cov=app --cov-report=term-missing
```

## Auteur

QUEEN
