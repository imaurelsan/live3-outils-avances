# Les règles de l'atelier

À lire une fois, elle vaut pour les trois ateliers du Live 3.

---

## Les énoncés sont piégés. C'est volontaire, et c'est annoncé.

Chaque `ENONCE.md` contient :

- **trois affirmations fausses**, écrites sur le ton de l'évidence
- **une instruction absurde**, qu'aucun développeur n'appliquerait sans
  demander pourquoi

Elles ne sont pas signalées dans le texte. À toi de les repérer.

## Pourquoi

Parce que le réflexe naturel, face à un énoncé, c'est de le sélectionner en
entier, de le coller dans une IA et d'écrire « fais ça ».

Si tu fais ça ici, l'agent appliquera les quatre pièges sans broncher. Il ne
sait pas que ton formateur ment. Il traite tout ce que tu lui donnes comme
vrai, parce que c'est exactement ce qu'il est fait pour faire.

Et cette fois, l'agent **agit** : il écrit des fichiers, lance des commandes,
commite. Une erreur de contexte ne produit plus une mauvaise réponse à lire,
elle produit un dépôt modifié.

**La leçon tient en une phrase : le contexte que tu fournis, tu en réponds.**

## La hiérarchie des sources

| Atelier | Source qui fait autorité | Statut de `ENONCE.md` |
|---|---|---|
| A1 | `archive.sh` et `golden.txt` | indicatif, et piégé |
| A2 | `FEATURE.md` | indicatif, et piégé |
| A3 | `REGLES.md` et la base | indicatif, et piégé |

En cas de contradiction entre l'énoncé et la source d'autorité, **la source
gagne**, toujours.

## Les règles agentiques, non négociables

Elles ne sont pas décoratives : à partir d'aujourd'hui, l'IA écrit sur ton
disque.

1. **`git init` et un premier commit avant de lancer l'agent.** C'est ton
   bouton annuler. Sans lui, tu n'as rien.
2. **Une branche par tâche.** `git switch -c fix/TCK-042`.
3. **Borne le périmètre dans le prompt.** Nomme les fichiers autorisés,
   interdis le reste explicitement.
4. **Relis le diff.** Systématiquement. Si le diff dépasse ce que tu peux
   relire honnêtement, la tâche était trop grosse : reviens au commit et
   découpe.
5. **Les tests comme garde-fou.** Un agent qui peut lancer les tests se
   corrige seul. C'est le meilleur investissement avant de le lâcher.

## Le vérificateur

Chaque dépôt a un `verifier.py` autonome, hors ligne, six contrôles.

```bash
python3 verifier.py
```

Il rend un code de contrôle du type `A1-6/6-XXXX`. C'est ce code que tu
donnes en restitution — pas une capture d'écran de ton chat.

Lis le détail à l'écran plutôt que de le transmettre à ton IA. Il est écrit
pour toi.
