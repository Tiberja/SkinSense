
CREATE TABLE hauttyp (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bezeichnung TEXT NOT NULL
);

CREATE TABLE kategorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    bezeichnung TEXT NOT NULL,
    beschreibung TEXT NOT NULL
);

CREATE TABLE produkt (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    beschreibung TEXT NOT NULL,
    name TEXT NOT NULL,
    preis NUMERIC NOT NULL,
    shop_link TEXT NOT NULL,
    inhaltsstoffe TEXT NOT NULL,
    anwendung TEXT NOT NULL
    bild TEXT NOT NULL
);

CREATE TABLE benutzer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    passwort_hash TEXT NOT NULL,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hauttyp_id INTEGER,
    FOREIGN KEY (hauttyp_id) REFERENCES hauttyp (id)
);

CREATE TABLE bewertung (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    produkt_id INTEGER,
    benutzer_id INTEGER,
    sterne INTEGER NOT NULL CHECK (sterne BETWEEN 1 and 5),
    kommentar TEXT NOT NULL,
    datum TEXT NOT NULL DEFAULT (date('now')),
    FOREIGN KEY (produkt_id) REFERENCES produkt (id) ON DELETE CASCADE,
    FOREIGN KEY (benutzer_id) REFERENCES benutzer (id) ON DELETE CASCADE
);

CREATE TABLE favorisiert (
    produkt_id INTEGER,
    benutzer_id INTEGER,
    PRIMARY KEY (produkt_id, benutzer_id),
    FOREIGN KEY (produkt_id) REFERENCES produkt (id) ON DELETE CASCADE,
    FOREIGN KEY (benutzer_id) REFERENCES benutzer (id) ON DELETE CASCADE
);

CREATE TABLE gehoert_zu (
    produkt_id INTEGER,
    kategorie_id INTEGER,
    PRIMARY KEY (produkt_id, kategorie_id),
    FOREIGN KEY (produkt_id) REFERENCES produkt (id) ON DELETE CASCADE,
    FOREIGN KEY (kategorie_id) REFERENCES kategorie (id) ON DELETE CASCADE
);

CREATE TABLE geeignet (
    produkt_id INTEGER,
    hauttyp_id INTEGER,
    PRIMARY KEY (produkt_id, hauttyp_id),
    FOREIGN KEY (produkt_id) REFERENCES produkt (id) ON DELETE CASCADE,
    FOREIGN KEY (hauttyp_id) REFERENCES hauttyp (id) ON DELETE CASCADE 
);

