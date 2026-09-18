# Live 3 — Coder par l'IA, outils avancés · 18/09/2026 · 15h–16h30

Trois ateliers, trois dépôts. Chacun a son `ENONCE.md` autonome et son
`verifier.py`.

| Dossier | Atelier | État initial | Durée |
|---|---|---|---|
| `demo-bash/` | A1 — porter un script bash en CLI Python | 0/6 | 25 min |
| `demo-depenses/` | A2 — ajouter une feature avec un agent | 2/6, 38 tests verts | 25 min |
| `demo-mcp/` | A3 — enchaîner plusieurs MCPs | 0/6, 6 tests verts | 25 min |

## Démarrer

```bash
pip install pytest

cd demo-bash     && python3 verifier.py    # A1-0/6
cd demo-depenses && pytest -q              # 38 passed
cd demo-mcp      && pytest -q              # 6 passed, et pourtant le bug est là
```

Python 3.10+. Aucune dépendance au-delà de pytest. A3 utilise `sqlite3`, qui
est dans la bibliothèque standard.

## Lis d'abord `REGLES-DU-JEU.md`

Les énoncés sont piégés, et c'est annoncé. Trois affirmations fausses et une
instruction absurde par fichier.

Ce n'est pas un piège à tricheurs : c'est une démonstration d'injection de
prompt en conditions réelles. Aujourd'hui, l'agent **agit** — une erreur de
contexte ne produit plus une mauvaise réponse à lire, elle produit un dépôt
modifié.

## Ce qui change par rapport au Live 2

Le Live 2 portait sur la conversation : on demande, on lit, on décide. Ici
l'IA a les mains sur le clavier.

Les trois ateliers montent en autonomie déléguée :

| Atelier | Ce que l'agent fait | Ton oracle |
|---|---|---|
| **A1** | boucle seule sur un `diff` | `golden.txt`, objectif et binaire |
| **A2** | touche quatre fichiers | 38 tests + le déterminisme |
| **A3** | lit trois sources, écrit, commite | la base, que les tests ne voient pas |

Le fil rouge :

> Un agent va aussi loin que l'oracle que tu lui donnes. Sans oracle, il
> tourne en rond et finit par déclarer que c'est fini.

En A3, `pytest` est vert au démarrage et le bug touche neuf clients. C'est la
démonstration la plus nette du live.

## Ce qu'on attend en restitution

- A1 : la ligne de sortie du bash avant portage
- A2 : le nombre de fichiers touchés par le diff
- A3 : le nombre d'appels d'outils de la chaîne complète
- Pour les trois : les notes fausses repérées, et les codes de contrôle

## Note

Données, code et tickets entièrement fictifs, écrits pour l'exercice.

`CORRECTION-animateur.md` contient les solutions, les pièges et les codes
tout-au-vert. À ne pas distribuer avant la restitution.
