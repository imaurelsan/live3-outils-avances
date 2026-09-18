#!/usr/bin/env bash
#
# archive.sh - archive et rotation des fichiers de log.
#
# Usage : ./archive.sh SOURCE DEST [JOURS]
#
# Deplace vers DEST/<date>/ tous les fichiers de SOURCE plus vieux que
# JOURS jours, ecrit un manifeste, puis ne garde que les 3 archives les
# plus recentes dans DEST.
#
# La date de reference est $REF_DATE (timestamp epoch) si elle est
# definie, sinon l'heure courante. Sans ca, rien n'est testable.

set -euo pipefail

SOURCE="${1:-}"
DEST="${2:-}"
JOURS="${3:-7}"
GARDER=3

if [ -z "$SOURCE" ] || [ -z "$DEST" ]; then
  echo "usage: $0 SOURCE DEST [JOURS]" >&2
  exit 64
fi

if [ ! -d "$SOURCE" ]; then
  echo "source introuvable: $SOURCE" >&2
  exit 66
fi

MAINTENANT="${REF_DATE:-$(date +%s)}"
LIMITE=$(( MAINTENANT - JOURS * 86400 ))
HORODATAGE=$(date -u -d "@$MAINTENANT" +%Y%m%d-%H%M%S)
CIBLE="$DEST/$HORODATAGE"

mkdir -p "$CIBLE"

deplaces=0
octets=0

while IFS= read -r -d '' fichier; do
  mtime=$(stat -c %Y "$fichier")
  if [ "$mtime" -ge "$LIMITE" ]; then
    continue
  fi
  taille=$(stat -c %s "$fichier")
  base=$(basename "$fichier")
  mv "$fichier" "$CIBLE/$base"
  deplaces=$(( deplaces + 1 ))
  octets=$(( octets + taille ))
done < <(find "$SOURCE" -maxdepth 1 -type f -name '*.log' -print0 | sort -z)

{
  echo "archive: $HORODATAGE"
  echo "source: $SOURCE"
  echo "limite: $LIMITE"
  echo "fichiers: $deplaces"
  echo "octets: $octets"
} > "$CIBLE/MANIFESTE.txt"

# rotation : on ne garde que les $GARDER archives les plus recentes
mapfile -t archives < <(find "$DEST" -mindepth 1 -maxdepth 1 -type d | LC_ALL=C sort -r)
supprimees=0
for (( i=GARDER; i<${#archives[@]}; i++ )); do
  rm -rf "${archives[$i]}"
  supprimees=$(( supprimees + 1 ))
done

echo "archive=$HORODATAGE fichiers=$deplaces octets=$octets purgees=$supprimees"

if [ "$deplaces" -eq 0 ]; then
  exit 1
fi
exit 0
