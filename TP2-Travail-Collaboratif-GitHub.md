# TP 2 guidé — Travail collaboratif & bonnes pratiques sur un dépôt GitHub

> **Public** : débutants/intermédiaires ayant suivi le [TP 1](./TP-CICD-DevSecOps.md) — niveau guidé pas-à-pas
> **Durée estimée** : 4 à 6 h (idéalement en **équipes de 2 à 4 personnes**)
> **Inspiré de** : le blog DevOps / DevSecOps de [Stéphane Robert](https://blog.stephane-robert.info/)
> **Stack** : Python (Flask) · Git · pre-commit · GitHub (Actions, PR, Rulesets) · Docker · Azure
> **Pré-requis** : avoir terminé le **TP 1** (le pipeline CI/CD y est construit ; ici on le réutilise dans un contexte d'équipe)

---

## 🎯 Objectifs pédagogiques

Le TP 1 vous a appris à construire **seul** un pipeline CI/CD DevSecOps. Le TP 2 vous apprend à travailler **à plusieurs** sur le même dépôt, proprement et en sécurité.

À la fin de ce TP, vous saurez :

1. Choisir et appliquer une **stratégie de branches** (GitHub Flow) adaptée à une équipe.
2. Adopter une convention de commits lisible (**Conventional Commits**).
3. Mettre en place des **hooks Git locaux** (`pre-commit`, `pre-push`) pour bloquer les erreurs **avant** le push.
4. **Gérer les secrets** correctement (jamais dans le code, détection automatique des fuites).
5. Collaborer via des **Pull Requests**, des **revues de code**, un fichier **CODEOWNERS** et des **templates**.
6. **Protéger la branche `main`** avec des règles (rulesets) : PR obligatoire, revue obligatoire, CI verte obligatoire.
7. Réutiliser le **même pipeline CI/CD que le TP 1** dans ce cadre collaboratif.
8. Gérer en équipe les situations réelles : **conflits de fusion**, branches synchronisées, historique propre.

---

## 🧰 Notions clés (à lire avant de commencer)

> 💡 **Travail collaboratif**
> Plusieurs personnes modifient le même code en parallèle. Sans règles, c'est le chaos : code écrasé, `main` cassée, secrets qui fuient. Les bonnes pratiques de ce TP servent à **rendre la collaboration sûre et fluide**.

> 💡 **Stratégie de branches (branching strategy)**
> Une convention qui dit *quelles branches existent*, *à quoi elles servent* et *comment on fusionne*. Elle évite que tout le monde travaille au même endroit en même temps.

> 💡 **Hook Git**
> Un script que Git exécute **automatiquement** à un moment précis (avant un commit, avant un push…). Un hook peut **bloquer** l'opération si quelque chose ne va pas. C'est un garde-fou **local**, qui agit avant même d'arriver sur GitHub.

> 💡 **Secret**
> Une donnée sensible : mot de passe, clé d'API, token, chaîne de connexion. Un secret commité reste **pour toujours** dans l'historique Git. La règle absolue : **un secret ne va jamais dans le code**.

> 💡 **Pull Request (PR)**
> Une demande de fusion d'une branche vers une autre. C'est le lieu de la **revue de code** : on relit, on commente, on approuve, et c'est là que la **CI** s'exécute. Rien n'entre dans `main` sans passer par une PR.

> 💡 **Revue de code (code review)**
> Un·e collègue relit votre code avant fusion. Ça attrape des bugs, partage la connaissance, et améliore la qualité. Une PR n'est fusionnée qu'**après approbation**.

### Les 3 lignes de défense (shift-left)

```
1) LOCAL (hooks pre-commit / pre-push)   ── le plus tôt, le plus rapide
        │  bloque lint/secrets/format AVANT le commit ou le push
        ▼
2) PULL REQUEST (CI GitHub Actions + revue humaine)
        │  tests + sécurité + relecture par un pair AVANT la fusion
        ▼
3) BRANCHE PROTÉGÉE (rulesets sur main)
        │  refuse tout ce qui n'a pas PR + revue + CI verte
        ▼
   main toujours propre, déployable et déployée (CI/CD du TP 1)
```

> 💡 **Pourquoi 3 lignes et pas une seule ?** Plus une erreur est attrapée tôt, moins elle coûte. Le hook local vous fait gagner du temps (pas d'aller-retour CI), la CI attrape ce que le local n'a pas vu, et la protection de branche garantit que **personne** ne contourne les règles.

### Schéma du flux collaboratif (GitHub Flow)

```
   main  ───●────────────────●──────────────●──────►  (toujours déployable)
            │                ▲              ▲
            │ branche        │ PR + revue   │ PR + revue
            │ feature/x      │ + CI verte   │ + CI verte
            └──●──●──●───────┘              │
                                           │
            │ branche                       │
            │ feature/y                     │
            └──────●──●──●──────────────────┘
```

---

## ✅ Prérequis

| Élément | Pourquoi |
|---|---|
| **TP 1 terminé** | On réutilise l'application Flask et le pipeline CI/CD |
| **Git** | Branches, hooks, commits |
| **Python 3.11+** | Lancer l'app, les tests, et `pre-commit` |
| **Compte GitHub** | Dépôt partagé, PR, Actions, rulesets |
| **VS Code** | Édition + extension GitLens (très utile en équipe) |
| **Docker Desktop** (optionnel) | Pour la partie build/scan d'image héritée du TP 1 |

> ✅ **Checkpoint prérequis** — Dans un terminal :
> ```bash
> git --version
> python --version      # ou python3 --version
> ```
> Et vous avez accès en écriture à un dépôt GitHub d'équipe (voir Étape 0).

---

# Étape 0 — Mettre en place le dépôt d'équipe

> 💡 Au TP 1, chacun **forkait** un dépôt et travaillait seul. Ici, **toute l'équipe travaille sur LE MÊME dépôt** (un seul dépôt partagé). C'est ce qui rend la collaboration réelle… et les règles nécessaires.

## 0.1 Créer (ou réutiliser) le dépôt partagé

Deux options selon votre contexte :

- **Option A (recommandée en formation)** : le formateur crée **une organisation GitHub** et **un dépôt par équipe**, puis ajoute les membres comme **collaborateurs** avec le rôle *Write*.
- **Option B** : un·e membre de l'équipe crée un dépôt personnel et invite les autres comme collaborateurs (**Settings → Collaborators → Add people**).

Le contenu de départ est celui du **TP 1 terminé** : l'application Flask, ses tests **et** le pipeline CI/CD (`ci.yml`, `cd.yml`). Ce TP 2 réutilise ce pipeline ; il ne le reconstruit pas. En revanche, les fichiers de **collaboration** (`.pre-commit-config.yaml`, `CODEOWNERS`, `.env.example`, template de PR, `CONTRIBUTING.md`) **ne doivent pas encore exister** : c'est vous qui allez les créer au fil du TP.

> 🌿 **Branches du dépôt de référence** : la branche **`starter`** contient le squelette de départ du **TP 1** (sans pipeline) ; la branche **`main`** contient la **solution complète des deux TP** (corrigé). Pour le TP 2, le bon point de départ est **« TP 1 terminé »** : soit votre dépôt après avoir fait le TP 1, soit un dépôt fourni par le formateur dans cet état.

> 📝 **Note pour le formateur** : préparez le dépôt d'équipe avec l'application, les tests et le pipeline du TP 1 **déjà en place**, mais **sans** les fichiers de collaboration listés ci-dessus (les apprenants les créeront). Le plus simple : faire jouer le TP 1 à l'équipe d'abord, puis enchaîner sur ce TP 2 sur le même dépôt.

## 0.2 Définir les rôles dans l'équipe

Pour ce TP, attribuez des rôles **tournants** (chacun jouera plusieurs rôles) :

| Rôle | Responsabilité |
|---|---|
| **Auteur·e** | Crée une branche, code, ouvre la PR |
| **Relecteur·trice (reviewer)** | Relit la PR, commente, approuve ou demande des changements |
| **Mainteneur·euse (maintainer)** | Veille à la propreté de `main`, configure les règles |

> 💡 La règle d'or du collaboratif : **on ne relit jamais sa propre PR**. C'est toujours un·e autre membre qui approuve.

> ⚠️ **Vous faites ce TP SEUL·E ?** GitHub **interdit d'approuver sa propre Pull Request**. Avec une règle « 1 approbation obligatoire » (Étape 7), vous ne pourriez **jamais** fusionner et vous seriez bloqué·e. Trois solutions :
> 1. **Recommandé** : créez un **2ᵉ compte GitHub** (ou faites-vous inviter un·e binôme) pour jouer le rôle de relecteur.
> 2. À l'Étape 7, mettez **Required approvals : 0** (vous gardez PR obligatoire + CI verte obligatoire, mais sans revue humaine).
> 3. Désactivez temporairement le ruleset le temps de fusionner.
> Les encadrés « 👤 En solo » de ce TP vous rappelleront quoi adapter.

## 0.3 Cloner le dépôt partagé

```bash
git clone https://github.com/<ORG-OU-USER>/<DEPOT>.git
cd <DEPOT>
code .
```

> ✅ **Checkpoint 0** — Chaque membre de l'équipe a cloné **le même** dépôt et peut faire `git pull` sans erreur.

---

# Étape 1 — La stratégie de branches (GitHub Flow)

> 💡 **GitHub Flow** : la stratégie la plus simple et la plus répandue. Une seule branche durable, `main`, **toujours déployable**. Tout le reste se fait dans des branches courtes de fonctionnalité (*feature branches*) fusionnées par PR.

## 1.1 Pourquoi pas tout le monde sur `main` ?

Imaginez 3 personnes qui poussent sur `main` en même temps : conflits permanents, `main` cassée, déploiements ratés. La solution : **chacun sa branche**, et `main` ne reçoit que du code **validé**.

## 1.2 La convention de nommage des branches

On nomme les branches de façon parlante, avec un **préfixe de type** :

```
feature/<courte-description>     # nouvelle fonctionnalité   → feature/ajout-route-stats
fix/<courte-description>         # correction de bug          → fix/erreur-404-tasks
chore/<courte-description>       # tâche technique            → chore/maj-dependances
docs/<courte-description>        # documentation              → docs/guide-contribution
```

> 💡 Bonnes pratiques de branche : **courte** (quelques jours max), **une seule chose** par branche, **partir de `main` à jour**.

## 1.3 Créer votre première branche de feature

```bash
git switch main
git pull                                  # toujours partir d'une main à jour
git switch -c feature/<votre-prenom>-bienvenue
```

> 🎯 **Exercice 1** — Chaque membre crée sa propre branche `feature/<prenom>-bienvenue`. Vérifiez avec `git branch` que vous êtes bien sur votre branche. **Ne poussez rien pour l'instant** — on configure d'abord les garde-fous (Étapes 2 à 4).

> ✅ **Checkpoint 1** — Chaque membre est sur sa propre branche de feature, partie d'une `main` à jour.

---

# Étape 2 — Convention de commits (Conventional Commits)

> 💡 **Conventional Commits** : une convention qui structure les messages de commit. Un historique lisible permet de comprendre *quoi* a changé et *pourquoi*, et même de générer des *changelogs* automatiquement.

## 2.1 Le format

```
<type>(<portée optionnelle>): <description courte à l'impératif>

[corps optionnel : pourquoi, détails]
```

Types courants :

| Type | Quand l'utiliser |
|---|---|
| `feat` | nouvelle fonctionnalité |
| `fix` | correction de bug |
| `docs` | documentation uniquement |
| `test` | ajout/modif de tests |
| `refactor` | réécriture sans changement de comportement |
| `chore` | maintenance, dépendances, config |
| `ci` | modification du pipeline CI/CD |

Exemples :

```
feat(api): ajoute la route GET /api/stats
fix(tasks): renvoie 404 quand la tâche n'existe pas
docs: ajoute un guide de contribution
ci: ajoute le scan de secrets dans la CI
```

> 💡 **À l'impératif présent** : « ajoute » et non « ajouté » / « ajout ». On décrit ce que **fait** le commit appliqué.

> 🎯 **Exercice 2** — Sans encore commiter, écrivez sur papier (ou dans le tchat d'équipe) le message Conventional Commit que vous utiliserez pour votre branche de bienvenue. Faites-le relire par un·e collègue.

---

# Étape 3 — Hooks Git locaux avec `pre-commit`

> 💡 **`pre-commit`** : un outil (en Python) qui gère des **hooks Git** de façon simple et partagée par toute l'équipe via un fichier de config versionné. Au lieu d'écrire des scripts shell à la main, on déclare des hooks dans `.pre-commit-config.yaml`.

> 💡 **Pourquoi un hook local ?** Il attrape les problèmes **avant** le commit/push : pas de CI rouge, pas d'aller-retour, pas de secret qui part sur GitHub. C'est la première ligne de défense.

## 3.1 Installer pre-commit

```bash
pip install pre-commit
pre-commit --version
```

## 3.2 Créer la configuration des hooks

Créez à la racine le fichier `.pre-commit-config.yaml` :

```yaml
# Hooks exécutés automatiquement avant chaque commit.
# Toute l'équipe partage exactement la même configuration (fichier versionné).
repos:
  # --- Hygiène de base des fichiers ---
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace        # supprime les espaces en fin de ligne
      - id: end-of-file-fixer          # garantit une ligne vide finale
      - id: check-yaml                 # vérifie la syntaxe des fichiers YAML
      - id: check-added-large-files    # bloque les fichiers trop volumineux
      - id: check-merge-conflict       # détecte les marqueurs de conflit oubliés

  # --- Lint + format Python (ruff, déjà connu du TP 1) ---
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff                       # lint
        args: [--fix]                  # corrige automatiquement ce qui peut l'être
      - id: ruff-format                # formatage du code

  # --- Détection de secrets (Gitleaks) : empêche une fuite AVANT le commit ---
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks
```

> 💡 On retrouve **ruff** (lint du TP 1) et **gitleaks** (scan de secrets du TP 1), mais cette fois **en local, avant le commit**. La même protection, plus tôt.

## 3.3 Activer les hooks

```bash
pre-commit install
```

Cette commande installe le hook dans `.git/hooks/`. **Important** : chaque membre de l'équipe doit lancer `pre-commit install` après le clone (les hooks ne se clonent pas automatiquement).

## 3.4 Tester les hooks sur tout le projet

```bash
pre-commit run --all-files
```

La première fois, pre-commit télécharge les outils (cela peut prendre une minute). Ensuite c'est quasi instantané.

> ⚠️ **Sous Windows (notamment en entreprise)** : à sa première exécution, le hook **gitleaks** télécharge un binaire. Derrière un **proxy d'entreprise**, ce téléchargement peut échouer avec une erreur peu claire. Si c'est le cas, installez gitleaks manuellement une fois (`winget install gitleaks`) ou assurez-vous que Docker Desktop est démarré, puis relancez `pre-commit run --all-files`.

> ✅ **Checkpoint 3** — `pre-commit run --all-files` se termine, et les hooks corrigent/valident vos fichiers. Si un hook modifie des fichiers (ex. `ruff-format`), réindexez-les (`git add`) avant de commiter.

> 🎯 **Exercice 3** — Faites votre premier commit avec hooks actifs :
> ```bash
> # Ajoutez une ligne "Contributeurs" dans le README avec votre prénom
> git add README.md
> git commit -m "docs: ajoute <prenom> aux contributeurs"
> ```
> Observez les hooks s'exécuter automatiquement **avant** que le commit soit accepté. Si un hook échoue, le commit est **bloqué** : corrigez, `git add`, et recommitez.

---

# Étape 4 — Hook `pre-push` : lancer les tests avant d'envoyer

> 💡 `pre-commit` peut aussi gérer le hook **`pre-push`**, qui s'exécute juste avant `git push`. On y met les vérifications un peu plus lentes qu'on ne veut pas lancer à chaque commit — typiquement **les tests**.

## 4.1 Ajouter un hook local de tests

Ajoutez ce bloc à la fin de `.pre-commit-config.yaml` :

```yaml
  # --- Hook local : lance pytest avant chaque push ---
  - repo: local
    hooks:
      - id: pytest-avant-push
        name: Tests pytest (avant push)
        entry: pytest -q
        language: system
        pass_filenames: false
        stages: [pre-push]      # ne s'exécute QUE lors d'un git push
```

> 💡 `repo: local` = un hook défini par vous (pas téléchargé). `stages: [pre-push]` = il ne tourne qu'au moment du push, pas à chaque commit (les tests seraient trop lents à chaque commit).

## 4.2 Activer le hook pre-push

`pre-commit install` n'installe par défaut que le hook de commit. Activez aussi le pre-push :

```bash
pre-commit install --hook-type pre-push
```

> 💡 Pour tout activer d'un coup à l'avenir :
> ```bash
> pre-commit install --hook-type pre-commit --hook-type pre-push
> ```

## 4.3 Pousser votre branche

```bash
git push -u origin feature/<votre-prenom>-bienvenue
```

Avant l'envoi, `pytest` s'exécute. Si un test échoue, **le push est annulé** : vous corrigez avant que GitHub ne voie quoi que ce soit.

> ✅ **Checkpoint 4** — Le push déclenche `pytest` localement. Avec des tests verts, la branche arrive sur GitHub. Avec un test rouge, le push est bloqué.

> 🎯 **Exercice 4** — Cassez volontairement un test (changez une assertion dans `tests/test_main.py`), tentez `git push`, et constatez que **le push est refusé**. Rétablissez le test, repoussez. Vous venez d'éviter une CI rouge.

> ⚠️ **À savoir** : un hook local peut être contourné (`git push --no-verify`). C'est pourquoi il **ne remplace pas** la CI ni la protection de branche (Étapes 6-7) — il les **complète**.

---

# Étape 5 — Gérer les secrets correctement

> 💡 La fuite de secrets est l'une des causes les plus fréquentes d'incident de sécurité. Au TP 1, on a vu Gitleaks en CI. Ici on adopte la **discipline complète** : où mettre les secrets, et comment ne jamais en commiter.

## 5.1 La règle absolue

**Un secret ne va JAMAIS dans le code ni dans Git.** À la place :

| Besoin | Où mettre le secret |
|---|---|
| En **local** (dev) | dans un fichier `.env` **ignoré par Git** |
| Dans la **CI/CD** | dans les **GitHub Secrets** (Settings → Secrets and variables → Actions) |
| Partagé en **équipe** | un gestionnaire de secrets (1Password, Vault, Azure Key Vault…) — **jamais** par mail/tchat |

## 5.2 Mettre en place le `.env` ignoré + un exemple versionné

Vérifiez que `.gitignore` contient bien `.env` (il y est depuis le TP 1). Puis créez un **modèle** versionné, **sans valeurs réelles** :

Fichier `.env.example` (celui-ci, on le commite) :

```
# Modèle de configuration. Copiez ce fichier en `.env` et remplissez les valeurs.
# Ne mettez JAMAIS de vraies valeurs ici : ce fichier est versionné.
SECRET_KEY=changez-moi-en-local
DATABASE_URL=postgresql://user:password@localhost:5432/app
```

Chaque membre fait ensuite, en local uniquement :

```bash
cp .env.example .env          # Windows PowerShell : Copy-Item .env.example .env
# puis édite .env avec ses vraies valeurs (ce .env n'est PAS commité)
```

> 💡 **Le combo gagnant** : `.env` (vraies valeurs, ignoré) + `.env.example` (modèle, versionné). Un nouvel arrivant sait immédiatement quelles variables remplir, sans qu'aucun secret ne fuite.

## 5.3 Le filet de sécurité : Gitleaks est déjà là

Vous l'avez branché en **pre-commit** (Étape 3) **et** il tourne en **CI** (TP 1). Double protection : un secret est bloqué localement, et même en cas de `--no-verify`, la CI le rattrape.

> ✅ **Checkpoint 5** — `.env` est ignoré par Git (`git status` ne le montre pas), et `.env.example` est versionné.

> 🎯 **Exercice 5** — Créez un fichier `config-test.py` contenant une fausse clé :
> ```python
> AWS_SECRET = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
> ```
> Tentez `git add config-test.py && git commit -m "test"`. Le hook **gitleaks doit bloquer le commit**. Supprimez le fichier.
>
> ⚠️ **Leçon** : si vous aviez utilisé `--no-verify`, le secret serait dans l'historique **pour toujours**. La seule vraie parade en cas de vraie fuite : **révoquer immédiatement le secret** (le considérer comme compromis) puis nettoyer l'historique.

---

# Étape 6 — Pull Requests & revue de code

> 💡 La PR est le cœur du travail collaboratif. C'est là que **la CI s'exécute** et que **les humains relisent**. Une bonne PR est petite, claire, et explique le *pourquoi*.

## 6.1 Ajouter un template de Pull Request

Un template pré-remplit la description de chaque PR pour qu'on n'oublie rien. Créez `.github/pull_request_template.md` :

```markdown
## Description
<!-- Que fait cette PR et pourquoi ? -->

## Type de changement
- [ ] feat (nouvelle fonctionnalité)
- [ ] fix (correction de bug)
- [ ] docs / test / chore / refactor / ci

## Checklist
- [ ] Les hooks pre-commit passent en local
- [ ] Les tests passent (`pytest`)
- [ ] Aucun secret n'est commité
- [ ] J'ai demandé une revue à un·e collègue

## Comment tester
<!-- Étapes pour vérifier le comportement -->
```

## 6.2 Définir des relecteurs avec CODEOWNERS

> 💡 **CODEOWNERS** : un fichier qui désigne automatiquement les relecteurs selon les fichiers modifiés. Quand une PR touche un fichier, son « propriétaire » est ajouté comme reviewer automatiquement.

Créez `.github/CODEOWNERS` (remplacez par les pseudos GitHub de l'équipe) :

```
# Chaque PR sera automatiquement assignée à ces relecteurs.
# Format : <motif de fichier>   <@utilisateur ou @org/équipe>

# Par défaut, toute l'équipe relit
*                   @membre1 @membre2

# Le pipeline est sensible : exiger une relecture dédiée
/.github/           @membre1
/Dockerfile         @membre1
```

> ⚠️ **Remplacez impérativement `@membre1` / `@membre2` par de VRAIS pseudos GitHub** de collaborateurs ayant accès au dépôt. Si un pseudo n'existe pas ou n'est pas collaborateur, GitHub considère le fichier comme **invalide** et l'ignore (au mieux), ou — si vous activez plus tard « Require review from Code Owners » — rend **toute fusion impossible** (personne ne peut fournir la revue exigée).
>
> 👤 **En solo** : n'activez **pas** « Require review from Code Owners » à l'Étape 7, sinon vous bloquerez vos propres PR.

## 6.3 Ouvrir une Pull Request

1. Poussez votre branche (déjà fait à l'Étape 4).
2. Sur GitHub, cliquez **Compare & pull request**.
3. La description est pré-remplie par votre template : complétez-la.
4. Vérifiez que **la CI démarre** (onglet checks de la PR) — c'est le pipeline du TP 1.
5. Un·e relecteur·trice est ajouté·e (via CODEOWNERS ou manuellement).

## 6.4 Faire une revue de code

Le ou la relecteur·trice :
- Ouvre l'onglet **Files changed**.
- Commente des lignes précises (bouton **+**).
- Choisit : **Approve**, **Comment**, ou **Request changes**.

> 💡 **Bonne revue** : on commente le **code**, pas la personne. On explique le *pourquoi* d'une suggestion. On approuve quand c'est correct, même imparfait (le mieux est l'ennemi du bien).

> ✅ **Checkpoint 6** — Une PR est ouverte avec description complète, la CI tourne dessus, et un·e collègue a laissé au moins un commentaire de revue.

> 🎯 **Exercice 6** — En binôme : A ouvre une PR, B la relit et demande un petit changement (**Request changes**). A pousse un nouveau commit sur la **même branche** (la PR se met à jour automatiquement, la CI se relance). B approuve.

---

# Étape 7 — Protéger la branche `main` (Rulesets)

> 💡 Tout ce qu'on a fait reste contournable tant que `main` n'est pas **protégée**. La protection rend les règles **obligatoires pour tout le monde**, y compris les admins si on le souhaite.

## 7.1 Créer un ruleset sur `main`

Sur GitHub : **Settings → Rules → Rulesets → New branch ruleset**.

- **Name** : `protection-main`
- **Enforcement status** : `Active`
- **Target branches** : `Include default branch` (cible `main`)
- Activez les règles suivantes :
  - ✅ **Require a pull request before merging** → définissez **Required approvals : 1** (au moins une revue). 👤 **En solo : mettez 0** (voir l'encadré de l'Étape 0).
  - ✅ **Require status checks to pass** → sélectionnez le check **« Lint & Tests »**. ⚠️ Voir l'avertissement ci-dessous avant d'ajouter les autres.
  - ✅ **Require branches to be up to date before merging**
  - ✅ **Block force pushes**

> ⚠️ **Choisir les bons status checks obligatoires.** Le nom affiché est celui du **job** (`Lint & Tests`, `SAST (Bandit)`, `Build & Scan image (Trivy)`…), pas l'identifiant YAML. Deux pièges :
> 1. Les checks n'apparaissent dans la liste **qu'après au moins une exécution** de la CI. Poussez une PR d'abord, sinon la liste est vide.
> 2. Ne rendez obligatoire que **« Lint & Tests »** (fiable). Le job **Trivy** peut échouer pour des CVE de l'image de base (hors de votre contrôle) et le bloquer en « required » empêcherait **toute** fusion. Vous l'ajouterez comme requis seulement quand il est stable.

> 💡 **Résultat concret** : impossible de pousser directement sur `main`, impossible de fusionner une PR sans **1 approbation** et sans **CI verte**. `main` est blindée.

> 💡 *Rulesets* vs *Branch protection rules* : les Rulesets sont la version moderne et plus flexible. Si votre dépôt ne propose pas encore les Rulesets, utilisez **Settings → Branches → Add rule** (mêmes options).

## 7.2 Vérifier que la protection fonctionne

```bash
git switch main
echo "test" >> README.md
git commit -am "test: tentative de push direct"
git push            # doit être REFUSÉ par GitHub
```

Annulez ce commit local de test :

```bash
git reset --hard origin/main
```

> ✅ **Checkpoint 7** — Le push direct sur `main` est **refusé**. Une PR sans approbation ou avec CI rouge ne peut **pas** être fusionnée (le bouton Merge est désactivé).

> 🎯 **Exercice 7** — Essayez de fusionner une PR **sans** approbation : le bouton est bloqué. Faites approuver par un·e collègue, attendez la CI verte, puis fusionnez. La protection a fait son travail.

---

# Étape 8 — Le pipeline CI/CD en contexte d'équipe

> 💡 **Objectif** : aboutir au **même pipeline CI/CD que le TP 1** (lint, tests, SAST, dépendances, secrets, build+scan image, puis déploiement Azure), mais branché sur le flux collaboratif qu'on vient de construire.

## 8.1 Réutiliser le pipeline du TP 1

Le dépôt contient déjà (depuis le TP 1) :
- `.github/workflows/ci.yml` — la CI complète (lint, tests, SAST Bandit, pip-audit, Gitleaks, build + Trivy)
- `.github/workflows/cd.yml` — le CD vers Azure (ACR + Web App)

Si ce n'est pas le cas, **copiez ces workflows depuis le TP 1** (Étapes 2 à 9 et Annexe A du TP 1).

## 8.2 La différence clé : la CI tourne sur les PR

Au TP 1, vous travailliez seul·e ; ici la CI est le **gardien des PR**. Grâce au ruleset (Étape 7), une PR ne peut être fusionnée que si **tous les status checks** du `ci.yml` sont verts. La CI n'est plus seulement informative : elle est **bloquante**.

> 💡 Rappel : le `ci.yml` du TP 1 se déclenche déjà sur `pull_request`. C'est exactement ce qu'il faut. Aucune modification n'est nécessaire — il s'intègre parfaitement au flux d'équipe.

## 8.3 Le CD se déclenche après fusion sur `main`

Le `cd.yml` ne se déclenche que sur `push` vers `main`. Comme on ne peut arriver sur `main` que **via une PR validée**, chaque déploiement correspond à du code **relu et testé**. C'est la garantie d'un déploiement sûr en équipe.

```
PR (feature/x) ──► CI verte ──► 1 approbation ──► Merge sur main ──► CD ──► Azure 🌐
```

## 8.4 (Optionnel mais recommandé) Approbation de déploiement

Reprenez l'**environnement protégé `production`** du TP 1 (Settings → Environments → `production` → Required reviewers). En équipe, c'est une **approval gate** : le déploiement attend qu'un·e mainteneur·euse valide.

> ✅ **Checkpoint 8** — Une PR fusionnée déclenche le CD ; l'application se redéploie sur Azure. Le pipeline complet du TP 1 fonctionne **dans le cadre collaboratif**.

> 💡 **Pas encore configuré Azure ?** Le `cd.yml` a besoin des secrets `AZURE_CREDENTIALS`, `ACR_LOGIN_SERVER` et `AZURE_WEBAPP_NAME` (créés à l'Étape 8 du TP 1). Sans eux, le job CD sera **rouge** dès `azure/login` — **c'est normal et ce n'est pas grave** : le CD se déclenche **après** la fusion (sur `push: main`), il ne tourne **pas** sur les Pull Requests, donc il **ne bloque jamais vos PR**. Concentrez-vous sur la CI (verte) ; activez le CD quand l'infra Azure du TP 1 est prête.

> 🎯 **Exercice 8** — En équipe : chaque membre ouvre une petite PR (ex. ajouter une route ou un test). Faites-les relire, fusionner l'une après l'autre, et observez les déploiements s'enchaîner. Vous venez de simuler une vraie journée d'équipe.

---

# Étape 9 — Gérer un conflit de fusion (situation réelle)

> 💡 Quand deux personnes modifient **les mêmes lignes** en parallèle, Git ne sait pas quoi garder : c'est un **conflit de fusion**. Savoir les résoudre sereinement est une compétence essentielle du travail en équipe.

## 9.1 Provoquer un conflit (en binôme)

1. **A** et **B** partent tous deux d'une `main` à jour et créent chacun une branche.
2. **A** et **B** modifient **la même ligne** du `README.md` (par exemple le titre), avec des textes différents.
3. **A** ouvre une PR, la fait valider, et la **fusionne** en premier.
4. **B** ouvre sa PR : GitHub indique **« This branch has conflicts »**.

> 👤 **En solo** : jouez les deux rôles. Depuis une `main` à jour, créez **deux** branches (`git switch -c conflit-a`, puis revenez sur main et `git switch -c conflit-b`). Modifiez la **même ligne** du README dans chacune. Fusionnez `conflit-a` en premier (via PR), puis ouvrez la PR de `conflit-b` : le conflit apparaît, et vous le résolvez avec la procédure 9.2.

## 9.2 Résoudre le conflit en local

**B** met sa branche à jour avec `main` et résout :

```bash
git switch feature/<branche-de-B>
git fetch origin
git merge origin/main          # le conflit apparaît
```

Git insère des marqueurs dans le fichier en conflit :

```
<<<<<<< HEAD
Titre proposé par B
=======
Titre proposé par A (déjà sur main)
>>>>>>> origin/main
```

Éditez le fichier pour **garder la bonne version** (supprimez les marqueurs `<<<<<<<`, `=======`, `>>>>>>>`), puis :

```bash
git add README.md
git commit -m "merge: résout le conflit du README avec main"   # finalise la fusion
git push
```

> ⚠️ **N'oubliez pas le `-m "..."`** : `git commit` tout seul ouvre un éditeur de texte (souvent **vim** sous Windows), où un débutant reste vite coincé. Avec `-m`, le message est fourni directement. (Pour sortir de vim si vous y êtes piégé : tapez `:q!` puis Entrée.)

La PR de **B** se met à jour, le conflit disparaît, la CI se relance.

> 💡 **Bonnes pratiques anti-conflits** : branches **courtes**, faire `git pull` sur `main` **souvent**, et synchroniser sa branche régulièrement (`git merge origin/main`). Plus on attend, plus les conflits sont gros.

> ✅ **Checkpoint 9** — Le conflit est résolu, la PR de B est fusionnable, et `main` contient une version cohérente.

> 🎯 **Exercice 9** — Refaites l'exercice en inversant les rôles. Cette fois, utilisez l'outil de résolution de conflits intégré à **VS Code** (boutons « Accept Current / Incoming / Both »).

---

# Étape 10 — Bonnes pratiques & pour aller plus loin

Vous avez un dépôt d'équipe sain. Voici comment le rendre « niveau pro ».

## 10.1 Templates d'issues

Créez `.github/ISSUE_TEMPLATE/bug_report.md` et `feature_request.md` pour standardiser les demandes. Une bonne issue = un bon point de départ pour une branche.

## 10.2 Guide de contribution

Un fichier `CONTRIBUTING.md` à la racine explique aux nouveaux arrivants : comment cloner, lancer `pre-commit install`, la convention de branches/commits, et le process de PR. **Gain de temps énorme** à chaque nouvel arrivant.

## 10.3 Signer ses commits

> 💡 Les commits signés (**Verified**) prouvent l'identité de l'auteur·e et empêchent l'usurpation. Voir [GitHub – signing commits](https://docs.github.com/authentication/managing-commit-signature-verification).

## 10.4 Maintenir `pre-commit` à jour

```bash
pre-commit autoupdate          # met à jour les versions des hooks
```

À committer dans une PR `chore: maj des hooks pre-commit`.

## 10.5 Stratégie de merge propre

Dans **Settings → General → Pull Requests**, choisissez en équipe :
- **Squash and merge** (recommandé) : un seul commit propre par PR sur `main`.
- Cochez **Automatically delete head branches** : nettoie les branches fusionnées.

## 10.6 Idées d'améliorations (mini-projets)

- **Dependabot + auto-merge** des mises à jour mineures (avec CI verte obligatoire).
- **Labels et milestones** pour organiser le travail.
- **GitHub Projects** (tableau Kanban) pour suivre l'avancement de l'équipe.
- **Branche `staging`** + environnement de pré-production avant `production`.
- **Commits signés obligatoires** via le ruleset.

---

## 🏁 Récapitulatif final

| Compétence collaborative | Outil / mécanisme | Étape |
|---|---|---|
| Dépôt partagé & rôles | Organisation / collaborateurs GitHub | 0 |
| Stratégie de branches | GitHub Flow | 1 |
| Messages de commit lisibles | Conventional Commits | 2 |
| Garde-fous locaux (lint, format, secrets) | pre-commit | 3 |
| Tests avant envoi | hook pre-push | 4 |
| Gestion des secrets | `.env` + `.env.example` + Gitleaks | 5 |
| Revue de code | Pull Requests, CODEOWNERS, templates | 6 |
| `main` inviolable | Rulesets (PR + revue + CI obligatoires) | 7 |
| Pipeline CI/CD d'équipe | GitHub Actions (réutilisé du TP 1) | 8 |
| Conflits de fusion | `git merge` + résolution | 9 |
| Pro-level | issues, CONTRIBUTING, signed commits, squash | 10 |

Bravo 👏 — vous savez maintenant collaborer **à plusieurs** sur un dépôt GitHub avec les mêmes garanties de qualité et de sécurité que le pipeline CI/CD du TP 1.

---

# Annexe A — Fichiers à créer (récapitulatif)

> 📝 Tous les fichiers de ce TP, prêts à copier.

### `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.6.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.6.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.4
    hooks:
      - id: gitleaks

  - repo: local
    hooks:
      - id: pytest-avant-push
        name: Tests pytest (avant push)
        entry: pytest -q
        language: system
        pass_filenames: false
        stages: [pre-push]
```

### `.env.example`

```
SECRET_KEY=changez-moi-en-local
DATABASE_URL=postgresql://user:password@localhost:5432/app
```

### `.github/pull_request_template.md`

```markdown
## Description

## Type de changement
- [ ] feat
- [ ] fix
- [ ] docs / test / chore / refactor / ci

## Checklist
- [ ] Hooks pre-commit OK en local
- [ ] Tests OK (`pytest`)
- [ ] Aucun secret commité
- [ ] Revue demandée

## Comment tester
```

### `.github/CODEOWNERS`

```
*           @membre1 @membre2
/.github/   @membre1
/Dockerfile @membre1
```

### `CONTRIBUTING.md`

```markdown
# Guide de contribution

1. Cloner le dépôt, puis : `pip install pre-commit && pre-commit install --hook-type pre-commit --hook-type pre-push`
2. Créer une branche : `git switch -c feature/<description>`
3. Commits au format Conventional Commits (`feat:`, `fix:`, `docs:`…)
4. Ouvrir une PR, attendre la CI verte + 1 approbation
5. Ne jamais pousser de secret (utiliser `.env`, ignoré par Git)
```

---

# Annexe B — Aide-mémoire des commandes (collaboratif)

```bash
# --- Branches ---
git switch main && git pull           # repartir d'une main à jour
git switch -c feature/ma-feature      # créer + aller sur une branche
git branch                            # lister les branches
git push -u origin feature/ma-feature # publier la branche

# --- Synchroniser / conflits ---
git fetch origin                      # récupérer l'état distant
git merge origin/main                 # intégrer main dans ma branche
git status                            # voir les fichiers en conflit

# --- pre-commit ---
pip install pre-commit
pre-commit install --hook-type pre-commit --hook-type pre-push
pre-commit run --all-files            # lancer tous les hooks manuellement
pre-commit autoupdate                 # mettre à jour les versions des hooks

# --- Secrets ---
cp .env.example .env                  # créer son .env local (jamais commité)
# Windows PowerShell : Copy-Item .env.example .env
gitleaks detect                       # scan manuel (nécessite le binaire gitleaks installé séparément)
```

> 💡 **Rappel des conventions** : branches `feature/`, `fix/`, `chore/`, `docs/` · commits `feat:`, `fix:`, `docs:`, `test:`, `ci:`, `chore:` · une PR = une chose, relue par un·e autre.

---

*Fin du TP 2. Vous savez maintenant travailler en équipe proprement et en sécurité. 🚀*
