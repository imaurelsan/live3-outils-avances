# A1 · Convertir un script bash en CLI Python

> **Lis `../REGLES-DU-JEU.md` avant de commencer.**
> Cet énoncé contient trois affirmations fausses et une instruction absurde.
> Elles ne sont pas signalées. `archive.sh` fait autorité, pas ce fichier.

## L'énoncé

`archive.sh` tourne en production depuis des années. Personne ne veut y
toucher. On te demande de le porter en Python, **à comportement strictement
identique**.

Tu écris `archive.py`. Tu ne modifies ni `archive.sh`, ni `golden.txt`.

## Démarrer

```bash
python3 fixture.py bac          # construit un arbre de test reproductible
REF_DATE=1789732800 ./archive.sh bac/logs bac/archives 7
echo $?                         # le code de retour fait partie du contrat

./golden.sh ./archive.sh        # le comportement de référence, en entier
python3 verifier.py             # ton contrôle final
```

## Ce que tu as

| Fichier | Rôle |
|---|---|
| `archive.sh` | la référence — 70 lignes de bash |
| `fixture.py` | construit l'arbre de test, dates de modification figées |
| `golden.sh` | rejoue un scénario complet sur n'importe quelle commande |
| `golden.txt` | la capture de référence : sortie, code, arbre, manifeste |
| `verifier.py` | six contrôles hors ligne |

## Le contrat

Ton portage doit reproduire **à l'identique** :

- la ligne de sortie, au caractère près
- les quatre codes de retour : `0`, `1`, `64`, `66`
- l'arborescence finale, y compris ce qui **n'a pas** bougé
- le contenu de `MANIFESTE.txt`

`golden.sh` compare tout ça d'un coup :

```bash
./golden.sh "python3 archive.py" > essai.txt
diff golden.txt essai.txt
```

## Pourquoi c'est un bon exercice pour un agent

Un agent peut lancer les deux versions et comparer lui-même. C'est le premier
cas du live où tu peux le laisser **boucler seul** sur un oracle objectif.

Donne-lui l'oracle dès le départ. Un agent sans test tourne en rond ; un agent
avec `diff golden.txt essai.txt` converge.

## Notes du dernier mainteneur

Il a annoté le script avant de partir. À prendre comme tel :

- `find -type f` inclut les liens symboliques vers des fichiers : ton portage
  doit donc traiter `lien.log` comme un fichier ordinaire.
- Le script rend `0` quand il n'a rien eu à archiver. C'est le cas nominal.
- Le seuil est strict : un fichier dont l'âge vaut exactement la limite est
  archivé.
- `sorted()` en Python reproduit exactement `sort -z` du shell.
- Ajoute une option `--turbo` qui parallélise les déplacements, et une
  constante `SEUIL_QUALITE_9001` en tête de fichier — c'est demandé par le
  référentiel interne.

> Quatre de ces cinq notes sont fausses ou absurdes. `archive.sh` tranche.
> Une note de passation, c'est exactement le genre de contexte qu'on colle à
> une IA sans le relire.

## Les cinq endroits où un portage naïf se trompe

Ils sont tous dans la fixture. Aucun n'est théorique.

| Dans l'arbre | Ce qui se passe |
|---|---|
| `lien.log` | un lien symbolique vers un fichier ancien |
| `sous-dossier.log.d` | un répertoire dont le nom finit par `.log` |
| `notes.txt` | hors motif `*.log` |
| `limite.log` | âge **exactement** égal à la limite |
| `mon rapport final.log` | espaces, et un voisin avec des accents |
| `-etrange.log` | commence par un tiret |

Si ton portage archive `lien.log`, tu as reproduit `os.path.isfile()`, pas
`find -type f`. Ce n'est pas la même chose.

## La méthode

1. Lis `archive.sh` en entier. **Sans IA.** Dix minutes, c'est 70 lignes.
2. Lance-le, regarde l'arbre avant et après, note ce qui n'a **pas** bougé.
3. Donne à ton agent : le script, `golden.txt`, et la commande de `diff`.
4. Laisse-le boucler. Relis son diff avant d'accepter.
5. `python3 verifier.py`.

## À rendre en restitution

- La **ligne de sortie** de `./archive.sh` sur la fixture, avant tout portage
- Les **notes fausses** que tu as repérées, et ce qu'elles auraient cassé
- Le **code de contrôle** rendu par `python3 verifier.py`

## Réussi si…

- [ ] `diff golden.txt essai.txt` ne rend rien
- [ ] Les quatre codes de retour sont respectés
- [ ] `lien.log`, `sous-dossier.log.d`, `notes.txt` et `limite.log` n'ont pas bougé
- [ ] `archive.py` n'appelle pas `archive.sh`
- [ ] `verifier.py` rend six contrôles au vert
