-- Schema de donnees/support.db, pour reference.

CREATE TABLE clients (
  id      INTEGER PRIMARY KEY,
  nom     TEXT NOT NULL,
  region  TEXT NOT NULL          -- IDF, RA, PACA, OCC, BZH
);

CREATE TABLE commandes (
  id                  INTEGER PRIMARY KEY,
  client_id           INTEGER NOT NULL,
  montant_cents       INTEGER NOT NULL,
  statut              TEXT NOT NULL,   -- livree, annulee, perdue, partielle
  jours_depuis_achat  INTEGER NOT NULL,
  FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE incidents (
  id           INTEGER PRIMARY KEY,
  commande_id  INTEGER NOT NULL,
  ouvert_le    TEXT NOT NULL,
  motif        TEXT NOT NULL,
  FOREIGN KEY (commande_id) REFERENCES commandes(id)
);
