
BEGIN TRANSACTION;

DELETE from geeignet;
DELETE from gehoert_zu;
DELETE from favorisiert;
DELETE from bewertung;
DELETE from benutzer;
DELETE from produkt;
DELETE from kategorie;
DELETE from hauttyp;

DELETE from sqlite_sequence;

--Hauttyp
INSERT INTO hauttyp (bezeichnung) VALUES ("trocken"); --1
INSERT INTO hauttyp (bezeichnung) VALUES ("oelig"); --2
INSERT INTO hauttyp (bezeichnung) VALUES ("normal"); --3
INSERT INTO hauttyp (bezeichnung) VALUES ("mischhaut"); --4
INSERT INTO hauttyp (bezeichnung) VALUES ("sensibel"); --5

--Kategorie 
INSERT INTO kategorie (bezeichnung, beschreibung) VALUES ("Reinigung","Entfernt Schmutz/Talg, ohne die Hautbarriere zu stressen."); --1
INSERT INTO kategorie (bezeichnung, beschreibung) VALUES ("Feuchtigkeitscreme","Spendet Feuchtigkeit, stärkt Barriere, reduziert Trockenheit/Glanz."); --2
INSERT INTO kategorie (bezeichnung, beschreibung) VALUES ("Sonnencreme","UV-Schutz (UVA/UVB) für Alltag; wichtig gegen Irritation & Aging."); --3
INSERT INTO kategorie (bezeichnung, beschreibung) VALUES ("Serum/Booster","Wirkstoff-Targeting (z. B. Niacinamid, Hyaluron, Ceramide."); --4
INSERT INTO kategorie (bezeichnung, beschreibung) VALUES ("Peeling","Sanftes AHA/BHA/PHA für Textur, Poren, Schüppchen (nicht täglich)."); --5

--Produkte
--trockene Haut
INSERT INTO produkt (beschreibung,name,preis,shop_link,inhaltsstoffe,anwendung,bild) VALUES ("Sanfter Gelreiniger für normale bis Mischhaut.","CeraVe Reinigungsgel","11,95 €","dm / Rossmann / Apotheke","Aqua, Glycerin, Ceramide, Niacinamid","Morgens & abends auf feuchte Haut einmassieren"); --1

INSERT INTO produkt (beschreibung,name,preis,shop_link,inhaltsstoffe,anwendung,bild) VALUES ("Sanfter Gelreiniger für normale bis Mischhaut.","CeraVe Reinigungsgel","11,95 €","dm / Rossmann / Apotheke","Aqua, Glycerin, Ceramide, Niacinamid","Morgens & abends auf feuchte Haut einmassieren","/static/images/products/CeraVe_Feuchtigkeitslotion.png"); --2

--Benutzer
INSERT INTO benutzer (passwort_hash,name,email,hauttyp_id) VALUES ("HASH1","Tiberja Gündüz","tiberja.gdz@gmail.com","1"); --1
INSERT INTO benutzer (passwort_hash,name,email,hauttyp_id) VALUES ("HASH2","Lina Kaufmann","lina.kfm@gmail.com","2"); --2

--Bewertung
INSERT INTO bewertung (produkt_id,benutzer_id,sterne,kommentar) VALUES ("2","2","4","sehr gutes Produkt"); --CeraVe Feuchtigkeitscreme

--Favoriten
INSERT INTO favorisiert (produkt_id,benutzer_id) VALUES ("2","2"); 

--gehört zu
--Reinigung

--Feuchtigkeitscremes
INSERT INTO gehoert_zu (produkt_id,kategorie_id) VALUES ("2","2"); --CeraVe Feuchtigkeitscreme

--Sonnencreme

--Serum/Booster

--Peeling


--geeignet
--trocken
INSERT INTO geeignet (produkt_id,hauttyp_id) VALUES ("1","1"); --CeraVe Feuchtigkeitscreme

--ölig

--normal

--mischhaut

--sensibel

COMMIT;



