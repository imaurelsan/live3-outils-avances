# Configurer les MCP de l'atelier

Trois serveurs, trois sources. C'est l'enchaînement qui compte, pas chaque
serveur pris isolément.

| Serveur | Ce qu'il apporte | Pour ce ticket |
|---|---|---|
| `filesystem` | lire `tickets/`, écrire `rapports/` | le *quoi* |
| `sqlite` | interroger `donnees/support.db` | le *qui* |
| git | branche, diff, commit | la trace |

Git passe par le shell de l'agent, pas par un MCP : tous les outils
agentiques du live savent déjà lancer des commandes.

## Claude Code

```bash
claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem "$PWD"
claude mcp add sqlite -- uvx mcp-server-sqlite --db-path "$PWD/donnees/support.db"
claude mcp list
```

## Cursor, Cline, Windsurf — `mcp.json`

Le fichier `exemple-mcp.json` de ce dossier est prêt à copier. Remplace
`CHEMIN_DU_DEPOT` par le chemin absolu du dépôt.

## Vérifier que ça répond

Avant de lancer quoi que ce soit, pose deux questions triviales à ton agent :

1. « Quels fichiers y a-t-il dans `tickets/` ? » → doit répondre sans lire le disque lui-même
2. « Combien de lignes dans la table `incidents` ? » → doit répondre 17

Si l'une des deux échoue, le serveur n'est pas branché. Ne commence pas le
ticket avant d'avoir les deux.

## Si rien ne s'installe

Repli sans MCP, qui garde tout l'intérêt de l'exercice : l'agent lit les
fichiers et lance `sqlite3` par le shell. Tu perds la démonstration du
protocole, pas celle de l'enchaînement des sources.

```bash
sqlite3 donnees/support.db "SELECT COUNT(*) FROM incidents;"
```

## Le point de sécurité

Un serveur MCP est du code tiers à qui tu donnes accès à tes fichiers et à ta
base. Regarde ce qu'il demande comme permissions avant de l'installer. Ici le
`filesystem` est limité au dépôt — c'est volontaire, et c'est le minimum.

C'est la capsule 7, en conditions réelles.
