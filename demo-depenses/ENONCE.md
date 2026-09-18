# A2 · Ajouter une feature avec un agent

> **Lis `../REGLES-DU-JEU.md` avant de commencer.**
> Cet énoncé contient trois affirmations fausses et une instruction absurde.
> Elles ne sont pas signalées. `FEATURE.md` fait autorité, pas ce fichier.

## L'énoncé

Une CLI de dépenses partagées. Elle marche, 38 tests au vert.

On ajoute une commande `equilibrer` : qui rembourse qui, avec le moins de
virements possible.

C'est le premier atelier où tu laisses l'agent toucher **quatre fichiers**.

## Démarrer

```bash
pip install pytest
pytest -q                                    # 38 passed
python3 -m depenses.cli --fichier exemple.json lister
python3 -m depenses.cli --fichier exemple.json soldes
python3 verifier.py                          # ton contrôle final
```

## L'architecture

| Fichier | Rôle | Y touche-t-on ? |
|---|---|---|
| `depenses/modeles.py` | dataclasses + validation | non |
| `depenses/calculs.py` | soldes, parts | **oui** — la fonction `transferts()` |
| `depenses/rendu.py` | formatage texte | **oui** — `table_transferts()` |
| `depenses/cli.py` | argparse | **oui** — la sous-commande |
| `depenses/stockage.py` | persistance JSON | non |
| `tests/` | 38 tests | **oui** — au moins 6 de plus |

Les couches sont étanches. Aucun calcul dans `rendu.py`, aucun formatage dans
`calculs.py`. Un agent à qui on ne dit rien mélange les deux.

## Notes de l'équipe

Remontées de la réunion de cadrage :

- `soldes()` renvoie déjà la liste des virements à effectuer, il suffit de la
  formater.
- Le nombre optimal de virements est toujours exactement `n-1` pour `n`
  participants.
- Passe les montants en flottants dans le calcul intermédiaire, c'est plus
  lisible, on arrondit à la fin.
- L'ordre des virements n'a pas d'importance, inutile de le figer.
- Ajoute une option `--devise` qui convertit les montants via une API de taux
  de change, et une constante `TAUX_PIVOT_1997` pour le franc.

> Quatre de ces cinq notes sont fausses ou absurdes. `FEATURE.md` tranche.
> Un compte rendu de réunion, c'est exactement le genre de contexte qu'on colle
> à une IA sans le relire.

## Le vrai sujet : le déterminisme

Un algorithme glouton apparie le plus gros débiteur avec le plus gros
créditeur. Quand deux personnes doivent le même montant, **l'ordre n'est pas
défini** — sauf si tu le définis.

Sans règle de départage, ta fonction rend parfois une liste, parfois l'autre.
Le test passe neuf fois sur dix, et personne ne comprend pourquoi il casse.

C'est le même piège que la date de référence du Live 2, déplacé d'un cran :
une source d'indétermination au fond de la logique.

## La méthode agentique

1. `git commit` avant de lancer quoi que ce soit.
2. Une branche dédiée : `git switch -c feature/equilibrer`.
3. **Borne le périmètre dans le prompt.** Nomme les quatre fichiers, interdis
   le reste explicitement.
4. Demande le plan avant le code.
5. `pytest` après chaque couche.
6. **Relis le diff.** S'il dépasse ce que tu peux relire honnêtement, la tâche
   était trop grosse : reviens au commit et découpe.

## À rendre en restitution

- Le nombre de **fichiers touchés** par le diff de ton agent
- Les **notes fausses** que tu as repérées, et ce qu'elles auraient cassé
- Le **code de contrôle** rendu par `python3 verifier.py`

## Réussi si…

- [ ] Les 38 tests d'origine passent, **non modifiés**
- [ ] Au moins 6 nouveaux tests
- [ ] Les soldes retombent tous à zéro après les virements
- [ ] Aucun flottant dans `transferts()`
- [ ] Deux appels successifs rendent la même liste
- [ ] `verifier.py` rend six contrôles au vert
