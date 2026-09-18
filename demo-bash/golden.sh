#!/usr/bin/env bash
# Capture le comportement de reference de archive.sh sur la fixture.
# Produit golden.txt : sortie, code de retour, arbre final, manifeste.
set -uo pipefail

CMD="${1:-./archive.sh}"
REF=1789732800
BAC=$(mktemp -d)
trap 'rm -rf "$BAC"' EXIT

python3 fixture.py "$BAC" >/dev/null

sortie=$(REF_DATE=$REF $CMD "$BAC/logs" "$BAC/archives" 7 2>&1)
code=$?

echo "=== SORTIE ==="
echo "$sortie"
echo "=== CODE ==="
echo "$code"
echo "=== ARBRE ==="
(cd "$BAC" && find . -mindepth 1 | LC_ALL=C sort)
echo "=== MANIFESTE ==="
cat "$BAC"/archives/*/MANIFESTE.txt 2>/dev/null | sed "s|$BAC|<BAC>|g"
echo "=== CAS LIMITES ==="
for essai in "manquant" "vide"; do
  case "$essai" in
    manquant) REF_DATE=$REF $CMD "$BAC/nexiste-pas" "$BAC/archives" 7 >/dev/null 2>&1 ;;
    vide)     mkdir -p "$BAC/neuf" && REF_DATE=$REF $CMD "$BAC/neuf" "$BAC/archives2" 7 >/dev/null 2>&1 ;;
  esac
  echo "$essai -> $?"
done
REF_DATE=$REF $CMD >/dev/null 2>&1; echo "sans-argument -> $?"
