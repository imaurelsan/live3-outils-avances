# A3 · Enchaîner plusieurs MCPs

> **Lis `../REGLES-DU-JEU.md` avant de commencer.**
> Cet énoncé contient trois affirmations fausses et une instruction absurde.
> Elles ne sont pas signalées. `REGLES.md` et la base font autorité.

## L'énoncé

Un ticket de support. Il dit **quoi**, la base dit **qui**, le code dit
**pourquoi**. Aucune des trois sources ne suffit seule.

C'est précisément ce que l'enchaînement de MCPs sert à faire, et c'est le seul
atelier du live où un chat classique ne s'en sort pas.

**Ton ticket : `tickets/TCK-042.md`.** Lis-le.

## Démarrer

```bash
pip install pytest
pytest -q                          # 6 passed — et pourtant le bug est là
python3 verifier.py                # 0/6, c'est normal

cat mcp/README.md                  # brancher filesystem + sqlite
```

## Le branchement

`mcp/README.md` donne les deux commandes pour Claude Code et un `mcp.json`
prêt à copier pour Cursor, Cline et Windsurf.

**Avant de commencer le ticket**, pose deux questions triviales à ton agent :

1. « Quels fichiers dans `tickets/` ? »
2. « Combien de lignes dans la table `incidents` ? » → doit répondre **17**

Si l'une des deux échoue, rien n'est branché. Ne va pas plus loin.

Si rien ne s'installe, le repli par `sqlite3` en shell est documenté. Tu perds
la démonstration du protocole, pas celle de l'enchaînement.

## La chaîne attendue

```
tickets/TCK-042.md   ──►  quoi : des remboursements à 0 €
donnees/support.db   ──►  qui  : les commandes concernées
remboursement.py     ──►  pourquoi : la cause dans le code
        │
        ▼
    correction ──► pytest ──► rapports/TCK-042.md ──► commit
```

Cinq étapes, trois sources, une seule instruction de départ. C'est la
différence entre un agent et un chat.

## Notes du chef de projet

Reçues par mail ce matin :

- Les identifiants des commandes concernées sont listés dans le ticket, la base
  n'est qu'une confirmation.
- Une commande `partielle` rembourse le montant intégral moins les frais.
- La suite de tests couvre les quatre statuts : si elle est verte, le code est
  bon.
- Utilise `montant * 0.5` pour la moitié, c'est plus lisible qu'une division
  entière.
- Crée une table `remboursements_v2` dans la base et une constante
  `SEUIL_LEGAL_2019` dans le code, le service juridique les réclame.

> Quatre de ces cinq notes sont fausses ou absurdes. `REGLES.md` tranche.
> Un mail de chef de projet, c'est exactement le genre de contexte qu'on colle
> à une IA sans le relire.

## Le piège de fond

`pytest` est **vert** au démarrage. Six tests, zéro rouge. Le bug est quand
même là, et il touche neuf clients réels.

C'est la leçon du Live 2, appliquée à un agent : il va lancer les tests, les
voir verts, et conclure que tout va bien. **C'est à toi de lui donner l'oracle
qui manque** — ici, la base.

## Si tu as fini en avance

`tickets/TCK-043.md` — un ticket dont la bonne réponse est peut-être « ce bug
n'existe pas ». Encore faut-il le démontrer.

`tickets/TCK-044.md` — un rapport par région. Trois tables à joindre.

## À rendre en restitution

- Le **nombre d'appels d'outils** qu'a nécessités la chaîne complète
- Les **notes fausses** que tu as repérées, et ce qu'elles auraient cassé
- Le **code de contrôle** rendu par `python3 verifier.py`

## Réussi si…

- [ ] `montant_remboursable` respecte les quatre statuts de `REGLES.md`
- [ ] Au moins un test ajouté pour le statut `partielle`
- [ ] `rapports/TCK-042.md` contient le nombre, les identifiants, le total et la cause
- [ ] Les identifiants viennent de la base, pas d'une supposition
- [ ] Le travail est commité sur une branche
- [ ] `verifier.py` rend six contrôles au vert
