from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Hauttyp(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    bezeichnung = db.Column(db.String, nullable=False)
    beschreibung = db.Column(db.String, nullable=False)

    benutzer = db.relationship('Benutzer', back_populates='hauttyp')
    produkte_geeignet = db.relationship('Produkt', secondary='geeignet', back_populates='geeignet_fuer')

class Kategorie(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    bezeichnung = db.Column(db.String, nullable=False)
    beschreibung = db.Column(db.String, nullable=False)
    produkte = db.relationship('Produkt', secondary='gehoert_zu', back_populates='kategorien')

class Produkt(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    name = db.Column(db.String, nullable=False)
    bezeichnung = db.Column(db.String, nullable=False)
    merkmale = db.Column(db.String, nullable=False)
    preis = db.Column(db.Numeric, nullable=False)
    beschreibung = db.Column(db.String, nullable=False)
    inhaltsstoffe = db.Column(db.String, nullable=False)
    anwendung = db.Column(db.String, nullable=False)
    shop_link = db.Column(db.String, nullable=False)
    bild = db.Column(db.String, nullable=False)

    bewertungen = db.relationship('Bewertung', back_populates='produkt', cascade='all, delete-orphan')
    kategorien = db.relationship('Kategorie', secondary='gehoert_zu', back_populates='produkte')
    geeignet_fuer = db.relationship('Hauttyp', secondary='geeignet', back_populates='produkte_geeignet')
    favorisiert_von = db.relationship('Benutzer', secondary='favorisiert', back_populates='favoriten')


class Benutzer(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)
    passwort_hash = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)

    hauttyp_id = db.Column(db.Integer, db.ForeignKey('hauttyp.id'), nullable=False)

    hauttyp = db.relationship('Hauttyp', back_populates='benutzer')
    bewertungen = db.relationship('Bewertung', back_populates='benutzer', cascade='all, delete-orphan')
    favoriten = db.relationship('Produkt', secondary='favorisiert', back_populates='favorisiert_von')



class Bewertung(db.Model):
    id = db.Column(db.Integer, primary_key=True, index=True)

    produkt_id = db.Column(db.Integer, db.ForeignKey('produkt.id', ondelete='CASCADE'))
    benutzer_id = db.Column(db.Integer, db.ForeignKey('benutzer.id', ondelete='CASCADE'))
    
    sterne = db.Column(db.Integer, nullable=False)
    kommentar = db.Column(db.String, nullable=False)
    datum = db.Column(db.String, nullable=False, server_default=db.text("(date('now'))"))

    produkt = db.relationship('Produkt', back_populates='bewertungen')
    benutzer = db.relationship('Benutzer', back_populates='bewertungen')


favorisiert = db.Table (
    'favorisiert',
    db.Column('produkt_id', db.Integer, db.ForeignKey('produkt.id', ondelete='CASCADE'), primary_key=True),
    db.Column('benutzer_id', db.Integer, db.ForeignKey('benutzer.id', ondelete='CASCADE'), primary_key=True)
)

gehoert_zu = db.Table (
    'gehoert_zu',
    db.Column('produkt_id', db.Integer, db.ForeignKey('produkt.id', ondelete='CASCADE'), primary_key=True),
    db.Column('kategorie_id', db.Integer, db.ForeignKey('kategorie.id', ondelete='CASCADE'), primary_key=True)
)

geeignet = db.Table (
    'geeignet',
    db.Column('produkt_id', db.Integer, db.ForeignKey('produkt.id', ondelete='CASCADE'), primary_key=True),
    db.Column('hauttyp_id', db.Integer, db.ForeignKey('hauttyp.id', ondelete='CASCADE'), primary_key=True)
)



