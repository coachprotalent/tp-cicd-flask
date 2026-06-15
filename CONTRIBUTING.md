# Guide de contribution

1. Cloner le dépôt, puis : `pip install pre-commit && pre-commit install --hook-type pre-commit --hook-type pre-push`
2. Créer une branche : `git switch -c feature/<description>`
3. Commits au format Conventional Commits (`feat:`, `fix:`, `docs:`…)
4. Ouvrir une PR, attendre la CI verte + 1 approbation
5. Ne jamais pousser de secret (utiliser `.env`, ignoré par Git)
