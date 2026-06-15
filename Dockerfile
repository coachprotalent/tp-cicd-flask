# ---- Étape 1 : build des dépendances ----
FROM python:3.12-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Étape 2 : image finale, minimale ----
FROM python:3.12-slim

# Créer un utilisateur non privilégié (ne jamais tourner en root)
RUN useradd --create-home --uid 1001 appuser

WORKDIR /app

# Copier seulement les dépendances installées + le code
COPY --from=builder /install /usr/local
COPY app/ ./app/

# Variables d'environnement
ENV PORT=8000 \
    PYTHONUNBUFFERED=1

USER appuser
EXPOSE 8000

# Serveur de production (gunicorn), pas le serveur de dev de Flask
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "app.main:app"]
