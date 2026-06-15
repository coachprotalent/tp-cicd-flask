# TP guidé — CI/CD & DevSecOps avec GitHub Actions et Azure

> **Public** : débutants en CI/CD — niveau guidé pas-à-pas
> **Durée estimée** : 4 à 6 h (réparties en plusieurs séances possibles)
> **Inspiré de** : le blog DevOps / DevSecOps de [Stéphane Robert](https://blog.stephane-robert.info/)
> **Stack** : Python (Flask) · pytest · GitHub Actions · Docker · Azure (ACR + Web App for Containers)

---

## 🎯 Objectifs pédagogiques

À la fin de ce TP, vous saurez :

1. Mettre en place un dépôt Git et travailler avec des **branches** et des **Pull Requests**.
2. Écrire et exécuter des **tests automatisés** (`pytest`).
3. Construire un **pipeline d'intégration continue (CI)** avec **GitHub Actions**.
4. Intégrer des contrôles **DevSecOps** : SAST, scan des dépendances, scan de secrets, scan d'image.
5. **Conteneuriser** une application avec Docker en suivant les bonnes pratiques.
6. Mettre en place un pipeline de **déploiement continu (CD)** vers **Azure**.
7. Appliquer les **bonnes pratiques** de sécurité et de qualité d'un vrai projet.

---

## 🧰 Notions clés (à lire avant de commencer)

> 💡 **CI (Continuous Integration / Intégration continue)**
> À chaque modification de code, une machine automatique récupère le code, l'analyse, le teste et signale les problèmes **avant** qu'ils n'arrivent en production. On « intègre » le travail de tous, souvent, en petites touches.

> 💡 **CD (Continuous Delivery / Deployment)**
> Une fois que le code passe tous les contrôles, il est automatiquement préparé (delivery) voire déployé (deployment) vers un environnement réel.

> 💡 **DevSecOps**
> On déplace la sécurité « à gauche » (*shift-left*) : au lieu de tester la sécurité à la fin, on l'intègre dès la CI. Chaque commit est analysé pour détecter des failles, des secrets oubliés, des dépendances vulnérables.

> 💡 **Pipeline**
> Une suite d'étapes automatiques (lint → tests → sécurité → build → déploiement). Si une étape échoue, le pipeline s'arrête : on ne déploie jamais du code cassé.

### Schéma du pipeline que nous allons construire

```
   Développeur
       │ git push / Pull Request
       ▼
┌─────────────────────────────────────────────────────────┐
│                  CI  (à chaque PR / push)                │
│  1. Lint (ruff)                                          │
│  2. Tests (pytest)                                       │
│  3. SAST (bandit)              ── DevSecOps              │
│  4. Scan dépendances (pip-audit)                         │
│  5. Scan secrets (gitleaks)                              │
│  6. Build image Docker + Scan image (trivy)             │
└─────────────────────────────────────────────────────────┘
       │ (uniquement si tout est vert, sur la branche main)
       ▼
┌─────────────────────────────────────────────────────────┐
│                  CD  (déploiement)                       │
│  7. Push de l'image vers Azure Container Registry (ACR)  │
│  8. Déploiement sur Azure Web App for Containers         │
└─────────────────────────────────────────────────────────┘
       │
       ▼
   Application en ligne 🌐
```

---

## ✅ Prérequis

Installez et créez les éléments suivants **avant** la première séance :

| Élément | Pourquoi | Lien |
|---|---|---|
| **Visual Studio Code** | Notre éditeur de code | https://code.visualstudio.com/ |
| **Git** | Gestion de versions | https://git-scm.com/ |
| **Python 3.11+** | Lancer l'application et les tests | https://www.python.org/ |
| **Docker Desktop** | Construire l'image conteneur | https://www.docker.com/products/docker-desktop/ |
| **Compte GitHub** | Héberger le code + GitHub Actions | https://github.com/ |
| **Compte Azure** | Déployer l'application (offre gratuite OK) | https://azure.microsoft.com/free/ |
| **Azure CLI (`az`)** | Créer les ressources Azure | https://learn.microsoft.com/cli/azure/install-azure-cli |

**Extensions VS Code recommandées** : `Python`, `Pylance`, `Docker`, `GitHub Actions`, `GitLens`, `YAML`.

> ✅ **Checkpoint prérequis** — Ouvrez un terminal et vérifiez :
> ```bash
> git --version
> python --version      # ou python3 --version
> docker --version
> az --version
> ```
> Chaque commande doit renvoyer un numéro de version sans erreur.

---

# Étape 0 — Mise en place du projet

## 0.1 Comprendre le fork

> 💡 **Fork** : une copie personnelle d'un dépôt GitHub existant, dans **votre** compte. Vous pouvez la modifier librement sans toucher à l'original.

1. Allez sur le dépôt **template** fourni par votre formateur (ex. `https://github.com/<FORMATEUR>/tp-cicd-flask`).
2. Cliquez sur le bouton **Fork** (en haut à droite).
3. Choisissez votre compte comme destination. Vous obtenez `https://github.com/<VOTRE-USER>/tp-cicd-flask`.

> 🌿 **Important — partez de la branche `starter`** : ce TP démarre d'un **squelette minimal** (l'application Flask + ses tests, **sans** le pipeline ni Docker — c'est vous qui allez les construire). Ce squelette est sur la branche **`starter`**. La branche **`main`** contient, elle, la **solution complète** (le corrigé) : n'y jetez un œil **qu'en cas de blocage**. Tout votre travail part de `starter`.

> 📝 **Note pour le formateur** : le dépôt de référence contient deux branches — **`main`** (solution complète / corrigé) et **`starter`** (squelette de départ). Pour que les apprenants démarrent du bon contenu, choisissez l'une de ces options :
> - **(Recommandé)** Dans **Settings → Branches**, définissez **`starter` comme branche par défaut** du dépôt à forker. Au fork, les apprenants seront automatiquement sur le bon contenu, et leur branche de travail (`main` ou `starter`) ne contiendra **pas** le corrigé.
> - Ou créez un **dépôt étudiant dédié** dont le `main` reprend le contenu de `starter` (ainsi toutes les mentions de `main` dans ce TP fonctionnent telles quelles).
>
> Le code de démarrage complet est aussi listé en [Annexe A](#annexe-a--code-de-démarrage-complet).

## 0.2 Cloner votre fork en local

Clonez **la branche `starter`** (le squelette de départ) :

```bash
git clone -b starter https://github.com/<VOTRE-USER>/tp-cicd-flask.git
cd tp-cicd-flask
code .          # ouvre le projet dans VS Code
```

> 💡 Si votre formateur a déjà fait de `starter` la branche par défaut, un simple `git clone https://github.com/<VOTRE-USER>/tp-cicd-flask.git` suffit (vous arriverez directement sur le bon contenu). Vérifiez avec `git branch` où vous vous trouvez.

## 0.3 Découvrir la structure du projet

```
tp-cicd-flask/
├── app/
│   ├── __init__.py
│   └── main.py            # l'application Flask
├── tests/
│   └── test_main.py       # les tests
├── requirements.txt       # dépendances de l'app
├── requirements-dev.txt   # dépendances de dev (tests, lint, sécurité…)
├── pyproject.toml         # configuration de ruff
├── .gitignore
└── README.md
```

> 💡 **C'est volontairement minimal** : pas de `.github/`, pas de `Dockerfile`. Vous allez créer ces fichiers étape par étape. C'est tout l'intérêt du TP : **construire** le pipeline, pas le recopier.

## 0.4 Créer un environnement virtuel et lancer l'app

> 💡 **Environnement virtuel** : un dossier isolé qui contient les dépendances de CE projet, pour ne pas polluer votre système.

```bash
# Création + activation
python -m venv .venv

# Activation - Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Activation - macOS / Linux
source .venv/bin/activate

# Installation des dépendances
pip install -r requirements.txt -r requirements-dev.txt

# Lancement de l'application
flask --app app.main run
```

Ouvrez http://127.0.0.1:5000/health dans votre navigateur.

> ✅ **Checkpoint 0** — Vous devez voir `{"status":"ok"}`.
> Testez aussi http://127.0.0.1:5000/api/tasks → vous devez voir une liste JSON de tâches.
> Arrêtez le serveur avec `Ctrl + C`.

## 0.5 La règle d'or : on ne pousse jamais sur `main` directement

À partir de maintenant, **chaque étape du TP se fait dans une branche dédiée**, puis on ouvre une **Pull Request (PR)**. C'est sur la PR que notre pipeline s'exécutera.

```bash
git checkout -b etape-1-tests
```

> 🎯 **Exercice 0** — Modifiez le `README.md` (ajoutez votre prénom dans une ligne « Auteur »), puis :
> ```bash
> git add README.md
> git commit -m "docs: ajoute l'auteur dans le README"
> git push -u origin etape-1-tests
> ```
> Sur GitHub, ouvrez la **Pull Request** proposée. Ne la fusionnez pas encore.

---

# Étape 1 — Les tests automatisés avec pytest

> 💡 **Pourquoi tester ?** Les tests vérifient automatiquement que le code fait ce qu'on attend. Quand on modifie le code plus tard, ils nous préviennent si on a cassé quelque chose. C'est le filet de sécurité de la CI.

## 1.1 Lire les tests existants

Ouvrez `tests/test_main.py`. Chaque fonction `test_...` vérifie un comportement de l'API.

## 1.2 Lancer les tests

```bash
pytest -v
```

Vous devez voir une liste de tests en vert (`PASSED`).

## 1.3 Mesurer la couverture de code

> 💡 **Couverture (coverage)** : le pourcentage de lignes de code exécutées par les tests. 100 % n'est pas obligatoire, mais une couverture faible signale des zones non testées.

```bash
pytest --cov=app --cov-report=term-missing
```

## 1.4 Écrire un nouveau test

L'API a une route `GET /api/tasks/<id>`. Ajoutez ce test dans `tests/test_main.py` :

```python
def test_get_single_task(client):
    response = client.get("/api/tasks/1")
    assert response.status_code == 200
    assert response.get_json()["id"] == 1


def test_get_unknown_task_returns_404(client):
    response = client.get("/api/tasks/9999")
    assert response.status_code == 404
```

Relancez `pytest -v`.

> ✅ **Checkpoint 1** — Tous les tests passent, y compris les deux nouveaux.

> 🎯 **Exercice 1** — Commitez votre travail :
> ```bash
> git add tests/test_main.py
> git commit -m "test: ajoute des tests sur la récupération d'une tâche"
> git push
> ```

---

# Étape 2 — Premier pipeline CI avec GitHub Actions

> 💡 **GitHub Actions** : le moteur d'automatisation intégré à GitHub. On décrit des **workflows** dans des fichiers YAML rangés dans `.github/workflows/`. GitHub les exécute automatiquement sur des machines (*runners*) selon des **déclencheurs** (push, pull request…).

### Vocabulaire YAML d'un workflow

```
workflow ──► jobs ──► steps
   │           │         └─ une commande ou une "action" réutilisable
   │           └─ s'exécute sur un runner (ex: ubuntu-latest)
   └─ déclenché par "on:" (push, pull_request…)
```

## 2.1 Créer le workflow CI

Créez le fichier `.github/workflows/ci.yml` :

```yaml
name: CI

# Déclencheurs : à chaque push et à chaque Pull Request
on:
  push:
    branches: [ "main" ]
  pull_request:

# Permissions minimales par défaut (bonne pratique de sécurité)
permissions:
  contents: read

jobs:
  lint-et-tests:
    name: Lint & Tests
    runs-on: ubuntu-latest
    steps:
      - name: Récupérer le code
        uses: actions/checkout@v4

      - name: Installer Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Installer les dépendances
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt -r requirements-dev.txt

      - name: Lint (ruff)
        run: ruff check .

      - name: Tests (pytest)
        run: pytest --cov=app --cov-report=term-missing
```

## 2.2 Pousser et observer

```bash
git add .github/workflows/ci.yml
git commit -m "ci: ajoute le workflow d'intégration continue"
git push
```

Sur GitHub, ouvrez l'onglet **Actions** (ou regardez votre Pull Request : la CI s'y affiche).

> 💡 **Lint** : `ruff` vérifie le style et détecte des erreurs de code sans l'exécuter. Du code propre = moins de bugs et plus facile à relire.

> ✅ **Checkpoint 2** — Le workflow « CI » apparaît avec une coche verte ✅. Cliquez dessus pour voir le détail de chaque étape.

> 🎯 **Exercice 2** — Introduisez volontairement une faute pour voir la CI échouer. Ajoutez tout en **haut** de `app/main.py` un import inutilisé :
> ```python
> import os   # ruff le détecte : F401 « importé mais jamais utilisé »
> ```
> Poussez, et observez la CI passer au **rouge** ❌. Lisez le message d'erreur de `ruff`, **supprimez la ligne**, repoussez. Vous venez de vivre la boucle de feedback de la CI !
>
> 💡 **Attention** : une variable inutilisée *au niveau module* (`x = 1`) n'est **pas** signalée par ruff. Utilisez un **import inutilisé** (règle F401) ou une variable inutilisée *à l'intérieur d'une fonction* (règle F841) — ceux-là sont bien détectés.

---

# Étape 3 — Sécurité du code : SAST avec Bandit

> 💡 **SAST (Static Application Security Testing)** : analyse le **code source** (sans l'exécuter) pour repérer des pratiques dangereuses : injections, usage de fonctions risquées, mots de passe en dur, etc. Pour Python, l'outil de référence est **Bandit**.

## 3.1 Tester Bandit en local

```bash
bandit -r app/
```

## 3.2 Ajouter un job SAST à la CI

Ajoutez ce job à la fin de `.github/workflows/ci.yml` (au même niveau d'indentation que `lint-et-tests:`) :

```yaml
  sast:
    name: SAST (Bandit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Installer Bandit
        run: pip install bandit

      - name: Analyse SAST du code
        run: bandit -r app/ -ll
```

> 💡 L'option `-ll` ne fait échouer le job que sur les alertes de gravité **moyenne ou haute**, pour éviter trop de bruit au début.

> ✅ **Checkpoint 3** — Après `git push`, deux jobs apparaissent désormais dans la CI : « Lint & Tests » et « SAST (Bandit) », tous deux verts.

> 🎯 **Exercice 3** — Ajoutez temporairement une ligne dangereuse dans `app/main.py`, par exemple :
> ```python
> import subprocess
> subprocess.call("ls", shell=True)   # Bandit va détecter shell=True
> ```
> Poussez, observez l'alerte Bandit en rouge, **puis supprimez cette ligne** et repoussez.

---

# Étape 4 — Sécurité des dépendances

> 💡 La majorité des failles d'une application proviennent de ses **dépendances** (les bibliothèques qu'on installe). Il faut donc les scanner et les tenir à jour. On combine deux approches : **pip-audit** (dans la CI) et **Dependabot** (les mises à jour automatiques).

## 4.1 Scan des dépendances avec pip-audit

Ajoutez ce job dans `.github/workflows/ci.yml` :

```yaml
  scan-dependances:
    name: Scan des dépendances (pip-audit)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
          cache: "pip"

      - name: Installer pip-audit
        run: pip install pip-audit

      - name: Auditer les dépendances
        run: pip-audit -r requirements.txt
```

## 4.2 Activer Dependabot

> 💡 **Dependabot** : un robot GitHub qui surveille vos dépendances et ouvre automatiquement des **Pull Requests** pour les mettre à jour quand une nouvelle version (ou un correctif de sécurité) sort.

Créez le fichier `.github/dependabot.yml` :

```yaml
version: 2
updates:
  # Mises à jour des dépendances Python (pip)
  - package-ecosystem: "pip"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  # Mises à jour des actions GitHub elles-mêmes
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "weekly"
```

> ✅ **Checkpoint 4** — Le job « Scan des dépendances » est vert. Le fichier `dependabot.yml` est sur GitHub (Dependabot s'activera tout seul ; vérifiez dans **Insights → Dependency graph → Dependabot**).

> 🎯 **Exercice 4** — Dans `requirements.txt`, remplacez la version de Flask par une **vieille version vulnérable** (ex. `flask==0.12.2`), poussez, et observez pip-audit signaler des CVE. **Remettez ensuite la version d'origine.**

---

# Étape 5 — Scan de secrets avec Gitleaks

> 💡 **Secret** : une information sensible (mot de passe, clé d'API, token). Un secret commité dans Git reste dans **l'historique pour toujours**, même si on le supprime ensuite. **Gitleaks** détecte ces fuites.

## 5.1 Ajouter le job de scan de secrets

Ajoutez dans `.github/workflows/ci.yml` :

```yaml
  scan-secrets:
    name: Scan de secrets (Gitleaks)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0          # nécessaire pour scanner tout l'historique

      - name: Gitleaks
        uses: gitleaks/gitleaks-action@v2
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

> ✅ **Checkpoint 5** — Le job « Scan de secrets » est vert (aucun secret détecté).

> 🎯 **Exercice 5** — Créez un fichier `secret-test.txt` contenant une fausse clé AWS :
> ```
> AKIAIOSFODNN7EXAMPLE
> aws_secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
> ```
> Commitez et poussez. Gitleaks doit faire **échouer** le pipeline. **Supprimez ensuite le fichier** et repoussez.
>
> ⚠️ **Leçon importante** : un vrai secret aurait fui ! La bonne pratique est de mettre les secrets dans les **GitHub Secrets** (jamais dans le code), et d'ajouter les fichiers sensibles (`.env`) au `.gitignore`.

---

# Étape 6 — Conteneurisation avec Docker

> 💡 **Conteneur** : un paquet qui embarque votre application **et** tout ce dont elle a besoin pour tourner (Python, dépendances, config). « Ça marche chez moi » → « ça marche partout ». L'**image** est le modèle figé ; le **conteneur** est une instance qui tourne.

## 6.1 Écrire le Dockerfile

Créez `Dockerfile` à la racine. On utilise un **build multi-stage** et un **utilisateur non-root** (bonnes pratiques de sécurité) :

```dockerfile
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
```

> 💡 **Pourquoi multi-stage ?** L'image finale ne contient pas les outils de compilation → elle est **plus petite** et **plus sûre** (moins de surface d'attaque).
> 💡 **Pourquoi non-root ?** Si un attaquant compromet le conteneur, il n'a pas les droits administrateur.
> 💡 **Pourquoi gunicorn ?** Le serveur intégré de Flask (`flask run`) est réservé au développement. En production on utilise un serveur WSGI robuste.

## 6.2 Ajouter le `.dockerignore`

Créez `.dockerignore` pour ne pas copier de fichiers inutiles/sensibles dans l'image :

```
.venv
__pycache__
*.pyc
.git
.github
tests
.env
*.md
```

## 6.3 Construire et tester l'image en local

```bash
docker build -t tp-cicd-flask:local .
docker run -p 8000:8000 tp-cicd-flask:local
```

Ouvrez http://127.0.0.1:8000/health → `{"status":"ok"}`.

> ✅ **Checkpoint 6** — L'application répond depuis le conteneur. Arrêtez avec `Ctrl + C`.

> 🎯 **Exercice 6** — Lancez `docker images` et notez la taille de votre image. Comparez avec une image basée sur `python:3.12` (sans `-slim`) : la version slim est bien plus légère.

---

# Étape 7 — Scan de l'image conteneur avec Trivy

> 💡 Une image Docker contient un mini système d'exploitation et des bibliothèques système qui peuvent, eux aussi, avoir des failles (CVE). **Trivy** scanne l'image et liste les vulnérabilités connues.

## 7.1 Ajouter le job de build + scan dans la CI

Ajoutez ce job dans `.github/workflows/ci.yml` :

```yaml
  build-et-scan-image:
    name: Build & Scan image (Trivy)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Construire l'image Docker
        run: docker build -t tp-cicd-flask:ci .

      - name: Scanner l'image avec Trivy
        uses: aquasecurity/trivy-action@0.28.0
        with:
          image-ref: tp-cicd-flask:ci
          format: table
          exit-code: "1"             # fait échouer le job si une faille est trouvée
          ignore-unfixed: true       # ignore les CVE sans correctif disponible
          severity: HIGH,CRITICAL    # n'échoue que sur les failles graves
```

> ✅ **Checkpoint 7** — Le job « Build & Scan image » construit l'image puis affiche le rapport Trivy. Avec une image `slim` récente, il doit être vert (ou ne lister que des CVE non corrigibles, ignorées).

> 💡 **Si ce job devient rouge** : ce n'est probablement **pas** votre faute. L'image de base `python:3.12-slim` peut accumuler de nouvelles CVE HIGH/CRITICAL au fil des semaines. C'est réaliste (en entreprise, on met à jour l'image de base). Pour ne pas bloquer le TP, vous pouvez temporairement passer `exit-code: "1"` à `exit-code: "0"` (le scan devient **informatif**), ou ajouter un fichier `.trivyignore` listant les CVE concernées.

> 🎯 **Exercice 7** — Lancez Trivy en local pour voir le rapport détaillé :
> ```bash
> docker build -t tp-cicd-flask:local .
> docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
>   aquasec/trivy image tp-cicd-flask:local
> ```

> 🏁 **Bilan CI** — Votre pipeline d'intégration continue est complet : **lint, tests, SAST, dépendances, secrets, build + scan image**. C'est déjà un vrai pipeline DevSecOps !

---

# Étape 8 — Préparer Azure (ressources + accès)

> 💡 On va maintenant déployer. Il faut d'abord **créer les ressources Azure** et donner à GitHub Actions le **droit** de les utiliser, de façon sécurisée.

> 📝 **Note** : ces commandes `az` peuvent être faites **une seule fois par le formateur** (ressources partagées) ou par chaque apprenant s'il a son propre abonnement. Remplacez les valeurs `<...>` et choisissez des noms **uniques** pour l'ACR et la Web App.

## 8.1 Se connecter et créer les ressources

> ⚠️ **Important (Windows)** — Les commandes ci-dessous utilisent la **syntaxe Bash** : variables `RG="..."`, suffixes aléatoires `$RANDOM`, substitution `$(...)`, et continuations de ligne avec `\`. Elles **ne fonctionnent pas telles quelles dans PowerShell**.
> Pour cette Étape 8, utilisez l'un de ces environnements :
> - **Azure Cloud Shell** (recommandé) : bouton `>_` dans le [portail Azure](https://portal.azure.com) — `az` y est déjà connecté et configuré ;
> - ou **Git Bash** / **WSL** sur votre poste Windows.
> Si vous préférez rester sous PowerShell, adaptez la syntaxe : `$RG = "rg-tp-cicd"`, `$ACR = "acrtpcicd$(Get-Random -Maximum 99999)"`, interpolation `"$($ACR).azurecr.io/..."`, et continuations avec un backtick `` ` `` au lieu de `\`.

```bash
# Connexion (ouvre le navigateur). Si pas de navigateur : az login --use-device-code
az login

# Variables (adaptez les noms — l'ACR et la Web App doivent être uniques au monde)
RG="rg-tp-cicd"
LOCATION="francecentral"
ACR="acrtpcicd$RANDOM"          # nom unique, minuscules/chiffres uniquement
PLAN="plan-tp-cicd"
APP="webapp-tp-cicd-$RANDOM"    # nom unique

# Groupe de ressources (un "dossier" qui regroupe tout)
az group create --name $RG --location $LOCATION

# Azure Container Registry (registre d'images privé)
az acr create --resource-group $RG --name $ACR --sku Basic --admin-enabled false

# Plan App Service (Linux) + Web App for Containers
az appservice plan create --resource-group $RG --name $PLAN --is-linux --sku B1
az webapp create --resource-group $RG --plan $PLAN --name $APP \
  --deployment-container-image-name "$ACR.azurecr.io/tp-cicd-flask:latest"

# Indiquer à la Web App le port exposé par notre conteneur
az webapp config appsettings set --resource-group $RG --name $APP \
  --settings WEBSITES_PORT=8000

echo "ACR = $ACR.azurecr.io"
echo "APP = $APP"
```

> 💡 **ACR (Azure Container Registry)** : un entrepôt privé pour vos images Docker, hébergé sur Azure. La Web App ira y chercher l'image à déployer.

## 8.2 Créer un compte de service pour GitHub (Service Principal)

> 💡 **Service Principal** : une « identité robot » qu'on donne à GitHub Actions pour qu'il agisse sur Azure **sans utiliser votre compte personnel**. On lui donne juste les droits nécessaires (principe du moindre privilège).

```bash
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

az ad sp create-for-rbac \
  --name "sp-github-tp-cicd" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RG \
  --sdk-auth
```

Cette commande affiche un **bloc JSON**. Copiez-le **entièrement** (de `{` à `}`).

## 8.3 Enregistrer les secrets dans GitHub

Sur votre dépôt GitHub : **Settings → Secrets and variables → Actions → New repository secret**. Créez :

| Nom du secret | Valeur |
|---|---|
| `AZURE_CREDENTIALS` | le bloc JSON copié à l'étape 8.2 |
| `ACR_LOGIN_SERVER` | `<ACR>.azurecr.io` (ex. `acrtpcicd1234.azurecr.io`) |
| `AZURE_WEBAPP_NAME` | le nom de la Web App (`$APP`) |

> ✅ **Checkpoint 8** — Les 3 secrets apparaissent dans GitHub (leur valeur est masquée). Les ressources `rg-tp-cicd`, votre ACR et votre Web App existent dans le portail Azure.

> ⚠️ **Sécurité** : ne collez **jamais** ce JSON dans le code ou dans un message. Il donne accès à Azure. C'est exactement le type de secret que Gitleaks (étape 5) cherche à empêcher de fuiter.

---

# Étape 9 — Déploiement continu (CD) vers Azure

> 💡 On crée un **second workflow** dédié au déploiement. Il ne se déclenche que sur la branche `main` (donc après fusion d'une PR validée). Il : se connecte à Azure → construit et pousse l'image vers l'ACR → déploie sur la Web App.

## 9.1 Créer le workflow CD

Créez `.github/workflows/cd.yml` :

```yaml
name: CD - Déploiement Azure

on:
  push:
    branches: [ "main" ]      # uniquement quand du code arrive sur main

permissions:
  contents: read

jobs:
  deploiement:
    name: Build, Push (ACR) & Deploy (Web App)
    runs-on: ubuntu-latest
    environment: production    # environnement protégé (voir 9.3)

    steps:
      - uses: actions/checkout@v4

      - name: Connexion à Azure
        uses: azure/login@v2
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Connexion à l'ACR
        run: az acr login --name ${{ secrets.ACR_LOGIN_SERVER }}

      - name: Définir le tag de l'image
        id: vars
        run: echo "tag=${{ secrets.ACR_LOGIN_SERVER }}/tp-cicd-flask:${{ github.sha }}" >> "$GITHUB_OUTPUT"

      - name: Build & Push de l'image vers l'ACR
        run: |
          docker build -t ${{ steps.vars.outputs.tag }} .
          docker push ${{ steps.vars.outputs.tag }}

      - name: Déploiement sur Azure Web App
        uses: azure/webapps-deploy@v3
        with:
          app-name: ${{ secrets.AZURE_WEBAPP_NAME }}
          images: ${{ steps.vars.outputs.tag }}
```

> 💡 **Pourquoi `github.sha` comme tag ?** Chaque déploiement utilise un tag unique (l'identifiant du commit). On sait toujours exactement quelle version est en ligne, et on peut revenir en arrière facilement.

## 9.2 Fusionner et déployer

1. Ouvrez une **Pull Request** de votre branche vers `main`. Vérifiez que **toute la CI est verte** ✅.
2. **Fusionnez** la PR (Merge).
3. Le push sur `main` déclenche automatiquement le workflow **CD**. Suivez-le dans l'onglet **Actions**.

## 9.3 (Bonne pratique) Protéger l'environnement de production

Dans GitHub : **Settings → Environments → New environment → `production`**. Activez **Required reviewers** et ajoutez-vous.

> 💡 Désormais, un déploiement en production **attend une validation humaine** avant de s'exécuter. C'est une *approval gate*, courante en entreprise.

> ✅ **Checkpoint 9** — Le workflow CD est vert. Ouvrez votre application en ligne :
> ```
> https://<AZURE_WEBAPP_NAME>.azurewebsites.net/health
> ```
> Vous devez voir `{"status":"ok"}`. 🎉 **Votre application est déployée automatiquement depuis GitHub !**

> 🎯 **Exercice 9** — Modifiez un message dans `app/main.py` (ex. le texte de la route `/`), faites une branche → PR → CI verte → merge. Observez le redéploiement automatique, puis rechargez l'URL Azure. Vous venez de faire une **mise en production de bout en bout** !

---

# Étape 10 — Bonnes pratiques & pour aller plus loin

Vous avez un pipeline complet. Voici comment le rendre « niveau pro ».

## 10.1 Protéger la branche `main`

**Settings → Branches → Add rule** sur `main` :
- ✅ Require a pull request before merging
- ✅ Require status checks to pass (sélectionnez les jobs de la CI)
- ✅ Require branches to be up to date

> 💡 Résultat : **impossible** de pousser directement sur `main` ou de fusionner une PR dont la CI est rouge.

## 10.2 Ajouter des badges au README

```markdown
![CI](https://github.com/<USER>/tp-cicd-flask/actions/workflows/ci.yml/badge.svg)
![CD](https://github.com/<USER>/tp-cicd-flask/actions/workflows/cd.yml/badge.svg)
```

## 10.3 Tester sur plusieurs versions de Python (matrice)

```yaml
  lint-et-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      # ... la suite identique
```

## 10.4 Idées d'améliorations (mini-projets)

- **OIDC au lieu d'un secret** : remplacer `AZURE_CREDENTIALS` par une connexion **OpenID Connect** (plus de secret long à stocker). [Doc Azure/OIDC](https://learn.microsoft.com/azure/developer/github/connect-from-azure).
- **Publier le rapport SARIF** de Trivy/Bandit dans l'onglet **Security** de GitHub (Code scanning).
- **Environnement de staging** avant la production.
- **Tests d'intégration** sur le conteneur lancé.
- **Versionnage sémantique** et création de *releases* GitHub.

---

## 🏁 Récapitulatif final

| Compétence | Outil | Étape |
|---|---|---|
| Tests automatisés | pytest | 1 |
| CI | GitHub Actions | 2 |
| Lint / qualité | ruff | 2 |
| SAST | Bandit | 3 |
| Dépendances | pip-audit + Dependabot | 4 |
| Secrets | Gitleaks | 5 |
| Conteneurisation | Docker (multi-stage, non-root) | 6 |
| Scan d'image | Trivy | 7 |
| Registry | Azure Container Registry | 8-9 |
| CD | GitHub Actions + Azure Web App | 9 |
| Bonnes pratiques | Branch protection, environments, OIDC | 10 |

Bravo 👏 — vous maîtrisez maintenant les fondations d'une chaîne **CI/CD DevSecOps** moderne.

---

# Annexe A — Code de démarrage complet

> 📝 Cette annexe contient **tous les fichiers** du dépôt template à forker. Le formateur crée le dépôt avec ces fichiers ; les apprenants le forkent à l'[Étape 0](#étape-0--mise-en-place-du-projet).

### `app/__init__.py`

```python
# Ce fichier (vide) fait de "app" un package Python.
```

### `app/main.py`

```python
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
```

### `tests/test_main.py`

```python
import pytest
from app.main import app


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    with app.test_client() as client:
        yield client


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_list_tasks(client):
    response = client.get("/api/tasks")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
    assert len(response.get_json()) >= 1


def test_create_task(client):
    response = client.post("/api/tasks", json={"title": "Nouvelle tâche"})
    assert response.status_code == 201
    assert response.get_json()["title"] == "Nouvelle tâche"
    assert response.get_json()["done"] is False


def test_create_task_without_title_returns_400(client):
    response = client.post("/api/tasks", json={})
    assert response.status_code == 400
```

### `requirements.txt`

```
Flask==3.1.3
gunicorn==23.0.0
```

### `requirements-dev.txt`

```
pytest==8.3.3
pytest-cov==5.0.0
ruff==0.6.9
bandit==1.7.10
pip-audit==2.7.3
```

### `.gitignore`

```
.venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
.env
*.log
```

### `pyproject.toml` (configuration de ruff)

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "W", "I"]   # erreurs, pyflakes, warnings, imports triés
```

### `README.md`

```markdown
# TP CI/CD — API de tâches (Flask)

Application support du TP CI/CD & DevSecOps.

## Lancer en local

\`\`\`bash
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
flask --app app.main run
\`\`\`

## Tester

\`\`\`bash
pytest -v
\`\`\`

## Auteur

- (votre prénom ici)
```

---

# Annexe B — Aide-mémoire des commandes

```bash
# --- Git ---
git checkout -b ma-branche        # créer + aller sur une branche
git add .                         # indexer les modifications
git commit -m "type: message"     # enregistrer un commit
git push -u origin ma-branche     # envoyer la branche sur GitHub

# --- Python / tests ---
python -m venv .venv              # créer l'environnement virtuel
pytest -v                         # lancer les tests
pytest --cov=app                  # avec la couverture
ruff check .                      # lint
bandit -r app/                    # SAST
pip-audit -r requirements.txt     # scan des dépendances

# --- Docker ---
docker build -t monimage:local .  # construire l'image
docker run -p 8000:8000 monimage:local   # lancer le conteneur
docker images                     # lister les images

# --- Azure ---
az login                          # se connecter
az group list -o table            # lister les groupes de ressources
az webapp log tail -g rg-tp-cicd -n <APP>   # voir les logs de la Web App
```

> 💡 **Convention de messages de commit** : `feat:` (fonctionnalité), `fix:` (correctif), `test:`, `ci:`, `docs:`, `refactor:`. Cela rend l'historique lisible.

---

*Fin du TP. Bon courage et amusez-vous bien ! 🚀*
