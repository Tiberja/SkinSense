import click
from flask_sqlalchemy import SQLAlchemy
from app import app

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///skinsense.sqlite"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy()
db.init_app(app)

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


with app.app_context():
    db.create_all()

@click.command('init-db')
def init():
    with app.app_context():
        db.drop_all()
        db.create_all()
    click.echo('Database has been initialized.')

app.cli.add_command(init) 

def insert_sample():
    #Tabellen leeren 
    db.session.execute(db.delete(geeignet))
    db.session.execute(db.delete(gehoert_zu))
    db.session.execute(db.delete(favorisiert))
    db.session.execute(db.delete(Bewertung))
    db.session.execute(db.delete(Benutzer))
    db.session.execute(db.delete(Produkt))
    db.session.execute(db.delete(Kategorie))
    db.session.execute(db.delete(Hauttyp))
    
    db.session.commit()
    
    # Hauttypen
    ht1 = Hauttyp(bezeichnung="Trockene Haut", beschreibung="gespannt, rau, schuppig")
    ht2 = Hauttyp(bezeichnung="Mischhaut", beschreibung="ölig in manchen Bereichen, trocken in anderen")
    ht3 = Hauttyp(bezeichnung="Ölige Haut", beschreibung="glänzend, sichtbare Poren")
    ht4 = Hauttyp(bezeichnung="Sensible Haut", beschreibung="reagiert schnell, leicht rot, gereizt")
    ht5 = Hauttyp(bezeichnung="Normale Haut", beschreibung="keine Auffälligkeiten")

    db.session.add_all([ht1, ht2, ht3, ht4, ht5])
    db.session.commit()

    # Kategorien
    k1 = Kategorie(bezeichnung="Reinigung", beschreibung="Reinigung ist der erste und wichtigste Schritt der Hautpflege. "
        "Sie entfernt Schmutz, Talg, Schweiß, Make-up und Umweltpartikel, "
        "die sich im Laufe des Tages auf der Haut ansammeln. "
        "Eine gute Reinigung beugt verstopften Poren, Pickeln und Entzündungen vor, "
        "ohne die Haut auszutrocknen oder zu reizen.")
    k2 = Kategorie(bezeichnung="Feuchtigkeitscreme", beschreibung="Feuchtigkeitscremes versorgen die Haut mit Wasser und helfen, dieses in der Haut zu speichern. "
        "Sie stärken die natürliche Hautbarriere, machen die Haut geschmeidig "
        "und verhindern Spannungsgefühle, Trockenheit oder übermäßigen Fettglanz. "
        "Auch fettige und unreine Haut braucht Feuchtigkeit, sonst produziert sie noch mehr Öl.")
    k3 = Kategorie(bezeichnung="Sonnencreme", beschreibung="Sonnencreme schützt die Haut vor schädlicher UV-Strahlung (UVA und UVB). "
        "Sie beugt vorzeitiger Hautalterung, Pigmentflecken und Hautschäden vor. "
        "Besonders wichtig ist Sonnenschutz bei Pickelmalen, Aknenarben oder empfindlicher Haut, "
        "da UV-Strahlen diese dunkler und langanhaltender machen können – auch im Alltag und bei bewölktem Himmel.")
    k4 = Kategorie(bezeichnung="Serum/Booster", beschreibung="Seren enthalten hochkonzentrierte Wirkstoffe und wirken gezielt auf bestimmte Hautprobleme. "
        "Je nach Inhaltsstoff können sie Unreinheiten reduzieren, Rötungen beruhigen, "
        "Feuchtigkeit spenden oder die Hautbarriere stärken. "
        "Ein Serum ergänzt die tägliche Pflege und verstärkt die Wirkung von Creme und Reinigung.")
    k5 = Kategorie(bezeichnung="Peeling", beschreibung="Peelings entfernen abgestorbene Hautschüppchen und sorgen für ein glatteres Hautbild. "
        "Chemische Peelings (AHA, BHA, PHA) können Poren reinigen, Pickel vorbeugen "
        "und das Verblassen von Pickelmalen unterstützen. "
        "Peelings sollten nicht täglich angewendet werden, da sie die Haut sonst reizen können.")

    db.session.add_all([k1, k2, k3, k4, k5])
    db.session.commit()

    # Produkte 
    p1 = Produkt(
        name="CeraVe Hydrating Cleanser", 
        bezeichnung="Cremiger Reiniger für trockene & empfindliche Haut", 
        merkmale="feuchtigkeitsspendend, parfumfrei, barriere-stärkend, nicht komedogen", 
        preis=8.95, 
        beschreibung="Sanfter, cremiger Reiniger, der Schmutz und leichte Rückstände entfernt, ohne die Haut auszutrocknen. Ideal bei Spannungsgefühl und trockener, empfindlicher Haut. Nach der Reinigung fühlt sich die Haut weich und gepflegt an, ohne zu spannen.", 
        inhaltsstoffe="Glycerin (Spendet Feuchtigkeit und verhindert ein trockenes oder spannendes Hautgefühl.) | Ceramide NP/AP/EOP (Stärken die natürliche Hautbarriere und helfen, Feuchtigkeit in der Haut zu halten.) | Sodium Hyaluronate (Hyaluronsäure, bindet Wasser und sorgt für ein hydratisiertes Hautgefühl.) | Cholesterol & Phytosphingosine (Unterstützen die Reparatur und Stabilität der Hautbarriere.) | Sodium Lauroyl Lactylate (Sehr mildes Reinigungsmittel, das die Haut sanft reinigt.) | Cetearyl/Cetyl/Stearyl Alcohol (Pflegende Fettalkohole, machen die Haut weich und trocknen sie nicht aus.) | Tocopherol (Vitamin E, schützt die Haut vor Umwelteinflüssen.) | Phenoxyethanol & Ethylhexylglycerin (Halten das Produkt hygienisch und sicher haltbar.)", 
        anwendung="Morgens & abends auf feuchter Haut einmassieren und abspülen.", 
        shop_link="https://www.dm.de/cerave-cerave-feuchtigkeitsspendende-reinigungslotion-p3337875597180.html", 
        bild="CeraVe_Feuchtigkeitsspendende_Reinigungslotion.png"
    )
    p2 = Produkt(
        name="La Roche-Posay Toleriane Reinigungsmilch",
        bezeichnung="Sehr milde Reinigungsmilch",
        merkmale="sehr sanft, parfumfrei, alkoholfrei, beruhigend",
        preis=17.95,
        beschreibung="Sehr milde Reinigungsmilch für trockene und hochsensible Haut, die schnell reagiert. Reinigt ohne starkes Schäumen und ist dadurch oft weniger austrocknend als Gelreiniger. Ideal, wenn die Haut nach dem Waschen zu Rötungen oder Spannungsgefühl neigt.",
        inhaltsstoffe="Glycerin (Spendet Feuchtigkeit und schützt die Haut vor dem Austrocknen.) | Thermalwasser von La Roche-Posay (Beruhigt empfindliche Haut und lindert Rötungen.) | Niacinamid (Stärkt die Hautbarriere und wirkt beruhigend.) | Caprylic/Capric Triglyceride (Pflegen die Haut und machen sie geschmeidig.) | Mildes Tensidsystem (Reinigt sanft, ohne die Haut zu reizen.) | Milde Konservierungsstoffe (Sorgen für Produktsicherheit bei sehr empfindlicher Haut.)",
        anwendung="Abends auftragen und mit Wattepad abnehmen oder sanft abspülen.",
        shop_link="https://www.dm.de/la-roche-posay-la-roche-posay-toleriane-reinigungsfluid-gesicht-und-augen-p3433422406599.html",
        bild="La_Roche_Posay_Toleriane_Reinigungsfluid.png"
    )
    p3 = Produkt(
        name="Eucerin UltraSensitive Reinigungslotion",
        bezeichnung="Reinigung ohne Duftstoffe",
        merkmale="reizarm, ultramild, parfumfrei, für hypersensible Haut",
        preis=13.95,
        beschreibung="Reinigungslotion für sehr empfindliche Haut, die möglichst wenig Reizpotenzial verträgt. Sie reinigt sanft und hilft dabei, Rötungen und Irritationen nicht zusätzlich zu triggern. Besonders geeignet, wenn du auf Duftstoffe oder „zu viel“ Pflege schnell reagierst.",
        inhaltsstoffe="Panthenol (beruhigt, unterstützt Regeneration)",
        anwendung="1–2× täglich sanft verteilen und abnehmen oder abspülen.",
        shop_link="https://www.shop-apotheke.com/beauty/8115115/eucerin-ultrasensitive-reinigungslotion-reduziert-roetungen-und-beruhigt-sehr-empfindliche-haut.htm",
        bild="Eucerin_UltraSensitive_Reinigungslotion.png"
    )
    p4 = Produkt(
        name="Balea Med Reinigungsmilch",
        bezeichnung="Milde Pflege für trockene Haut",
        merkmale="parfumfrei, sanft, preiswert, feuchtigkeitserhaltend",
        preis=2.95,
        beschreibung="Alltags-Reinigungsmilch für trockene und empfindliche Haut zum sehr günstigen Preis. Reinigt mild und ist darauf ausgelegt, die Haut nicht „quietschig sauber“ zu entfetten. Gut für alle, die eine unkomplizierte Reinigung ohne Schnickschnack wollen.",
        inhaltsstoffe="Glycerin (zieht Wasser an), Panthenol (beruhigt und schützt)",
        anwendung="Täglich morgens und/oder abends anwenden, danach abspülen oder abnehmen.",
        shop_link="https://www.dm.de/balea-med-reinigungsmilch-ultra-sensitive-p4066447429220.html",
        bild="Balea_Reinigungsmilch.png"
    )
    p5 = Produkt(
        name="Avène Extremely Gentle Cleanser",
        bezeichnung="Ultra-milde Reinigung",
        merkmale="sehr verträglich, beruhigend, reizarm, für sehr trockene Haut",
        preis=16.95,
        beschreibung="Ultra-sanfter Cleanser für sehr empfindliche, trockene oder gereizte Haut. Die Formulierung ist bewusst minimalistisch gehalten und häufig auch dann angenehm, wenn andere Reiniger brennen. Ideal als „Sicherheitsprodukt“, wenn die Hautbarriere gerade gestresst ist.",
        inhaltsstoffe="Avène Thermalwasser (beruhigt, entzündungshemmend)",
        anwendung="Morgens & abends sanft auftragen; optional abspülen oder mit Tuch abnehmen.",
        shop_link="https://www.shop-apotheke.com/beauty/16537506/avene-tolerance-reinigungslotion.htm",
        bild="Avene_Tolerance_Reinigungslotion.png"
    )
    p6 = Produkt(
        name="CeraVe Feuchtigkeitscreme",
        bezeichnung="Reichhaltige Pflege für trockene Haut",
        merkmale="reichhaltig, parfumfrei, barriere-stärkend, langanhaltend",
        preis=14.95,
        beschreibung="Reichhaltige Creme für trockene bis sehr trockene Haut, die intensiv pflegt und die Hautbarriere unterstützt. Sie ist besonders praktisch, weil sie für Gesicht und Körper genutzt werden kann. Viele mögen sie, weil sie spürbar glättet und Trockenheitsstellen über den Tag hinweg reduziert.",
        inhaltsstoffe="Ceramide (reparieren Barriere), Hyaluronsäure (speichert Feuchtigkeit), Glycerin (reduziert Wasserverlust)",
        anwendung="1–2× täglich auf die gereinigte Haut auftragen.",
        shop_link="https://www.dm.de/cerave-feuchtigkeitscreme-p3337875597395.html",
        bild="CeraVe_Feuchtigkeitscreme.png"
    )
    p7 = Produkt(
        name="Eucerin UreaRepair PLUS 5%",
        bezeichnung="Intensivpflege gegen Trockenheit",
        merkmale="intensiv feuchtigkeitsspendend, glättend, barriere-stützend",
        preis=18.95,
        beschreibung="Intensivpflege, die speziell bei sehr trockener, rauer oder schuppiger Haut hilft. Urea kann Trockenheit spürbar reduzieren und die Haut wieder geschmeidiger machen. Besonders gut geeignet im Winter oder wenn die Haut zu „Krokodilhaut“-Gefühl neigt.",
        inhaltsstoffe="Urea 5% (natürlicher Feuchthaltefaktor, glättet), Ceramide (stärken Hautbarriere)",
        anwendung="Abends oder nach Bedarf auftragen, besonders auf trockene Stellen.",
        shop_link="https://www.dm.de/eucerin-urearepair-plus-5-p4005800218686.html",
        bild="Eucerin_UreaRepair_PLUS.png"
    )
    p8 = Produkt(
        name="La Roche-Posay Lipikar Baume AP+M",
        bezeichnung="Sehr reichhaltige Pflege",
        merkmale="sehr reichhaltig, beruhigend, barriere-stärkend, rückfettend",
        preis=19.95,
        beschreibung="Sehr reichhaltiger Balm für trockene bis sehr trockene und empfindliche Haut. Er pflegt intensiv, reduziert Spannungsgefühl und unterstützt die Barriere langfristig. Besonders beliebt als „Winterrettung“ oder bei Haut, die schnell rau und gereizt wird.",
        inhaltsstoffe="Sheabutter (rückfettend, schützt), Niacinamid (stärkt Barriere, beruhigt)",
        anwendung="1× täglich (oder nach Bedarf) auftragen.",
        shop_link="https://www.dm.de/la-roche-posay-lipikar-baume-ap-m-p3337875751033.html",
        bild="LaRochePosay_Lipikar_Baume_AP.png"
    )
    p9 = Produkt(
        name="Weleda Skin Food Light",
        bezeichnung="Natürliche Pflege für trockene Haut",
        merkmale="natürliche Pflege, pflegend, leichter als Classic, duftend",
        preis=8.95,
        beschreibung="Leichtere Version der klassischen Skin Food – pflegend, aber nicht ganz so schwer auf der Haut. Gut, wenn du natürliche Öle und Kräuterextrakte magst und eine Creme suchst, die Trockenheit mildert. Durch den Duft ist sie eher etwas für Personen, die Duftstoffe gut vertragen.",
        inhaltsstoffe="Sonnenblumenöl (nährt und schützt), Kamille (beruhigend)",
        anwendung="Täglich auftragen, besonders auf trockene Partien.",
        shop_link="https://www.dm.de/weleda-skin-food-light-p4001638500525.html",
        bild="Weleda_Skin_Food_Light.png"
    )
    p10 = Produkt(
        name="Avène Hydrance RICH",
        bezeichnung="Feuchtigkeitspflege für sehr trockene Haut",
        merkmale="reichhaltig, beruhigend, feuchtigkeitsspendend, für sensible Haut",
        preis=18.95,
        beschreibung="Feuchtigkeitscreme, die speziell für trockene bis sehr trockene, empfindliche Haut gedacht ist. Sie versorgt die Haut spürbar mit Feuchtigkeit und macht sie weicher, ohne sofort wieder „zu verschwinden“. Ideal morgens, wenn du tagsüber weniger Spannungsgefühl haben möchtest.",
        inhaltsstoffe="Sheabutter (schützt vor Austrocknung), Thermalwasser (beruhigt, mindert Reizungen)",
        anwendung="Morgens auf die gereinigte Haut auftragen.",
        shop_link="https://www.dm.de/avene-hydrance-rich-p3282779317231.html",
        bild="Avene_Hydrance_UVRiche.png"
    )
    p11 = Produkt(
        name="La Roche-Posay Anthelios Hydrating Cream SPF50+",
        bezeichnung="Reichhaltiger Sonnenschutz für trockene & empfindliche Haut",
        merkmale="SPF50+, feuchtigkeitsspendend, hoher UVA/UVB-Schutz, für sensible Haut",
        preis=18.95,
        beschreibung="Reichhaltige Sonnencreme für trockene und empfindliche Haut, die sich eher wie Pflege anfühlt. Sie bietet sehr hohen UVA- und UVB-Schutz und kann Spannungsgefühl durch Trockenheit reduzieren. Gut geeignet, wenn viele matte Fluids dir zu austrocknend sind.",
        inhaltsstoffe="Mexoryl SX/XL (moderne UV-Filter, hoher UVA/UVB-Schutz), Glycerin (bindet Feuchtigkeit), Thermalwasser (beruhigt)",
        anwendung="Morgens als letzten Schritt großzügig auftragen und bei Bedarf nachlegen.",
        shop_link="https://www.dm.de/la-roche-posay-anthelios-hydrating-cream-spf50-p3337875588875.html",
        bild="LaRochePosay_Anthelios_Hydrating_Cream50+.png"
    )
    p12 = Produkt(
        name="Eucerin Sensitive Protect SPF50+",
        bezeichnung="Sonnenschutz speziell für trockene & sensible Haut",
        merkmale="SPF50+, reizarm, antioxidativ, feuchtigkeitsspendend",
        preis=17.95,
        beschreibung="Sonnenschutz, der speziell auf empfindliche und trockene Haut ausgelegt ist. Schützt zuverlässig vor UVA/UVB-Strahlen und hilft durch antioxidative Inhaltsstoffe, UV-bedingten Stress abzufedern. Wenn du schnell Brennen bekommst, ist das oft eine angenehme Option.",
        inhaltsstoffe="Licochalcone A (antioxidativ, schützt vor UV-Stress), Glycerin (Feuchtigkeit), UV-Filter (UVA/UVB-Schutz)",
        anwendung="Morgens großzügig auftragen, bei Sonne regelmäßig erneuern.",
        shop_link="https://www.dm.de/eucerin-sensitive-protect-spf50-p4005800301622.html",
        bild="Eucerin_Sensitive_Protect.png"
    )
    p13 = Produkt(
        name="Nivea UV Gesicht Sensitive SPF50",
        bezeichnung="Pflegender Sonnenschutz ohne Duftstoffe",
        merkmale="SPF50, parfumfrei, pflegend, alltagstauglich",
        preis=8.95,
        beschreibung="Alltagstauglicher Sonnenschutz fürs Gesicht mit hoher Schutzleistung, der ohne Duftstoffe auskommt. Besonders interessant, wenn du eine günstige Option suchst, die nicht brennt und gleichzeitig etwas pflegt. Gut für empfindliche Haut, die schnell reagiert.",
        inhaltsstoffe="Vitamin E (Antioxidans), Glycerin (Feuchtigkeit), UV-Filter (UVA/UVB-Schutz)",
        anwendung="Morgens großzügig auftragen, bei Bedarf erneuern.",
        shop_link="https://www.dm.de/nivea-uv-gesicht-sensitive-spf50-p4005900463125.html",
        bild="Nivea_UVGesicht_sensitive.png"
    )
    p14 = Produkt(
        name="Bioderma Photoderm Creme SPF50+",
        bezeichnung="Sehr hoher Sonnenschutz für trockene Haut",
        merkmale="SPF50+, sehr schützend, feuchtigkeitsspendend, reichhaltig",
        preis=19.95,
        beschreibung="Sehr hoher Sonnenschutz mit cremiger, eher reichhaltiger Textur – passend für trockene Haut, die unter vielen Sonnenfluids spannt. Der Fokus liegt auf zuverlässigem Schutz und zusätzlicher Pflege. Wenn du es gerne cremig magst, ist das eine gute Option.",
        inhaltsstoffe="Cellular Bioprotection™ (zellschützendes Konzept), Glycerin (spendet Feuchtigkeit)",
        anwendung="Morgens großzügig auftragen, bei Sonne regelmäßig nachlegen.",
        shop_link="https://www.dm.de/bioderma-photoderm-creme-spf50-p3401579428378.html",
        bild="Bioderma_Photoderm_Creme.png"
    )
    p15 = Produkt(
        name="The Ordinary Hyaluronic Acid 2% + B5",
        bezeichnung="Intensives Feuchtigkeitsserum für trockene Haut",
        merkmale="feuchtigkeitsspendend, aufpolsternd, vegan, leicht",
        preis=8.95,
        beschreibung="Leichtes Feuchtigkeitsserum, das der Haut schnell „Wasser“ gibt und Trockenheitsfältchen optisch glatter wirken lassen kann. Sehr gut unter einer Creme, weil es die Haut aufnahmefähiger macht. Ideal, wenn du Feuchtigkeit willst, ohne ein schweres Gefühl.",
        inhaltsstoffe="Hyaluronsäure (bindet Wasser, polstert auf), Vitamin B5 (beruhigt, unterstützt Regeneration)",
        anwendung="Morgens & abends vor der Creme auf leicht feuchter Haut auftragen.",
        shop_link="https://www.douglas.de/de/p/3001047392",
        bild="TheOrdinary_Hyaluronic_Acid.png"
    )
    p16 = Produkt(
        name="Vichy Minéral 89",
        bezeichnung="Stärkendes Feuchtigkeitsserum",
        merkmale="barriere-stärkend, hydratisierend, schnell einziehend",
        preis=21.95,
        beschreibung="Ein sehr leichtes Serum, das die Hautbarriere unterstützen und gleichzeitig intensiv hydratisieren soll. Viele nutzen es als „Basis-Serum“ morgens oder abends, weil es schnell einzieht und sich gut kombinieren lässt. Besonders angenehm, wenn die Haut müde und trocken wirkt.",
        inhaltsstoffe="Hyaluron (intensive Hydration), Thermalwasser (stärkt, beruhigt)",
        anwendung="Täglich morgens und/oder abends vor der Creme auftragen.",
        shop_link="https://www.dm.de/vichy-mineral-89-p3337875597425.html",
        bild="Vichy_Mineral89_Boost.png"
    )
    p17 = Produkt(
        name="Balea Hyaluron Booster",
        bezeichnung="Günstiges Feuchtigkeitsserum",
        merkmale="preiswert, feuchtigkeitsspendend, beruhigend",
        preis=3.95,
        beschreibung="Sehr günstiger Feuchtigkeitsbooster für den Alltag, der Trockenheitsgefühl reduzieren kann. Gut als Einstieg, wenn du Hyaluron testen willst, ohne viel Geld auszugeben. Lässt sich leicht unter Creme und Make-up tragen.",
        inhaltsstoffe="Hyaluronsäure (Feuchtigkeit), Panthenol (beruhigt und schützt)",
        anwendung="Täglich vor der Creme auftragen.",
        shop_link="https://www.dm.de/balea-hyaluron-booster-p4058172776792.html",
        bild="Balea_Hyaluron_Booster.png"
    )
    p18 = Produkt(
        name="Eucerin Hyaluron-Filler Moisture Booster",
        bezeichnung="Intensiver Feuchtigkeitsbooster",
        merkmale="sehr leicht, feuchtigkeitsspendend, aufpolsternd",
        preis=18.95,
        beschreibung="Leichter Moisture-Booster, der schnell einzieht und die Haut praller wirken lassen kann. Ideal, wenn du Feuchtigkeit möchtest, aber keine schwere Creme-Schicht. Besonders praktisch am Morgen oder unter Sonnencreme.",
        inhaltsstoffe="Hyaluron (polstert Trockenheitsfältchen), Glycerin (hält Feuchtigkeit in der Haut)",
        anwendung="Morgens vor der Creme/Sonnencreme auftragen.",
        shop_link="https://www.dm.de/eucerin-hyaluron-filler-moisture-booster-p4005800238370.html",
        bild="Eucerin_Hyaluron_Filler_Boost_Serum.png"
    )
    p19 = Produkt(
        name="The Ordinary Lactic Acid 5% + HA",
        bezeichnung="Sanftes AHA-Peeling für trockene Haut",
        merkmale="mild exfolierend, glättend, feuchtigkeitsspendend",
        preis=10.19,
        beschreibung="Sehr sanftes AHA-Peeling für trockene Haut, das abgestorbene Hautschüppchen löst und die Haut glatter wirken lässt. Milchsäure ist im Vergleich zu stärkeren AHAs oft verträglicher und kann zusätzlich Feuchtigkeit unterstützen. Ideal, wenn du ein Peeling willst, aber Angst vor Reizung hast.",
        inhaltsstoffe="Lactic Acid 5% (AHA) (Sanftes chemisches Peeling, entfernt abgestorbene Hautzellen und sorgt für ein glatteres Hautbild.) | Tasmanian Pepperberry (Reduziert mögliche Reizungen und Rötungen durch das Peeling.) | Sodium Hyaluronate (Hyaluronsäure, spendet Feuchtigkeit und beugt Trockenheit vor.) | Glycerin (Unterstützt die Feuchtigkeitsbindung und schützt vor Spannungsgefühlen.) | pH-optimierte Formulierung (Sorgt dafür, dass das Peeling effektiv, aber möglichst hautschonend wirkt.)",
        anwendung="1–2× pro Woche abends auftragen, danach Creme verwenden.",
        shop_link="https://www.douglas.de/de/p/3001043645",
        bild="TheOrdinary_Lactic_Acid.png"
    )
    p20 = Produkt(
        name="Paula's Choice Calm 1% BHA Lotion",
        bezeichnung="Sehr mildes Peeling für trockene & empfindliche Haut",
        merkmale="sehr mild, porenklärend, beruhigend",
        preis=32.95,
        beschreibung="Sehr mild formulierte BHA-Lotion, die Poren klären kann, ohne die Haut stark zu stressen. Durch die niedrige Dosierung ist sie häufig besser verträglich als klassische 2% BHA-Produkte. Gut, wenn du empfindliche Haut hast, aber trotzdem gegen verstopfte Poren arbeiten willst.",
        inhaltsstoffe="Salicylsäure 1% (klärt Poren sanft), Haferextrakt (beruhigt, mindert Rötungen)",
        anwendung="Abends dünn auftragen, langsam einschleichen.",
        shop_link="https://www.douglas.de/de/p/3001047420",
        bild="Paulas_Choice_calm.png"
    )
    p21 = Produkt(
        name="Balea Beauty Expert PHA Toner",
        bezeichnung="Sehr mildes chemisches Peeling",
        merkmale="sehr sanft, feuchtigkeitsspendend, preiswert",
        preis=4.95,
        beschreibung="Sehr mildes Peeling-Toner-Konzept, das die Hautoberfläche glätten kann, ohne stark zu reizen. PHAs sind meist sanfter als viele AHAs und werden oft gut von trockener, empfindlicher Haut vertragen. Ideal, wenn du „ein bisschen Peeling“ für mehr Glow möchtest.",
        inhaltsstoffe="PHA (mildes Peeling, bindet zusätzlich Feuchtigkeit)",
        anwendung="2× wöchentlich nach der Reinigung anwenden.",
        shop_link="https://www.dm.de/balea-beauty-expert-pha-toner-p4058172776518.html",
        bild="balea_pha_toner.png"
    )
    p22 = Produkt(
        name="Avène Gentle Peeling Gel",
        bezeichnung="Mechanisch-enzymatisches Peeling",
        merkmale="sehr mild, beruhigend, für sensible Haut",
        preis=17.95,
        beschreibung="Sanftes Peeling-Gel mit sehr feinen Partikeln, das abgestorbene Hautschüppchen lösen kann, ohne stark zu rubbeln. Durch die milde Ausrichtung ist es eher für empfindliche Haut gedacht als klassische grobe Scrubs. Gut, wenn du ein weiches Hautgefühl möchtest, aber wenig Risiko eingehen willst.",
        inhaltsstoffe="Celluloseperlen (feine Peelingpartikel), Thermalwasser (beruhigt)",
        anwendung="1× pro Woche auf feuchter Haut sanft massieren und abspülen.",
        shop_link="https://www.dm.de/avene-gentle-peeling-p3282770111960.html",
        bild="Avene_gentle_Peeling.png"
    )
    p23 = Produkt(
        name="Eucerin DermoPure Soft Scrub",
        bezeichnung="Mildes Peeling für trockene & unreine Haut",
        merkmale="sanft, glättend, porenfreundlich",
        preis=13.95,
        beschreibung="Mildes Peeling, das sowohl gegen raue Haut als auch gegen Unreinheiten unterstützen kann, ohne zu aggressiv zu sein. Durch feine Partikel wird die Hautoberfläche geglättet, während Milchsäure zusätzlich sanft exfolieren kann. Gut, wenn du trocken bist, aber trotzdem zu verstopften Poren neigst.",
        inhaltsstoffe="Milchsäure (Lactic Acid) (Löst abgestorbene Hautschüppchen und beugt verstopften Poren vor.) | Sanfte Peelingpartikel (Entfernen überschüssigen Talg und glätten die Hautoberfläche.) | Glycerin (Spendet Feuchtigkeit und schützt vor Austrocknung.) | Salicylsäure (BHA) (Wirkt antibakteriell und hilft gegen Pickel und Unreinheiten.) | Entzündungshemmende Inhaltsstoffe (Beruhigen unreine und zu Akne neigende Haut.)",
        anwendung="1× wöchentlich sanft einmassieren und abspülen.",
        shop_link="https://www.dm.de/eucerin-dermopure-waschpeeling-p4005800238127.html",
        bild="Eucerin_DermoPure_Waschpeeling.png"
    )
    p24 = Produkt(
        name="CeraVe Reinigungsgel",
        bezeichnung="Sanfter Gelreiniger für normale bis Mischhaut",
        merkmale="sanft reinigend, parfumfrei, barriere-stärkend, für Mischhaut geeignet",
        preis=11.95,
        beschreibung="Sanfter Gelreiniger für normale bis Mischhaut, der gründlich reinigt ohne die Haut auszutrocknen. Ideal, wenn die T-Zone schneller glänzt, die Wangen aber eher trocken sind. Die Haut fühlt sich nach dem Waschen sauber, aber nicht „quietschig“ oder spannig an.",
        inhaltsstoffe="Ceramide (stärken Hautbarriere, verhindern Feuchtigkeitsverlust), Niacinamid (reguliert Talg, beruhigt Rötungen), Glycerin (bindet Wasser in der Haut)",
        anwendung="Morgens & abends auf feuchte Haut einmassieren und abspülen.",
        shop_link="https://www.dm.de/cerave-reinigungsgel-p3337875597357.html | https://www.rossmann.de/de/pflege-und-duft-cerave-reinigungsgel/p/3337875597357",
        bild="CeraVe_Reinigungsgel.png"
    )
    p25 = Produkt(
        name="Balea Med Ultra Sensitive Waschgel",
        bezeichnung="Seifenfreier Reiniger ohne Duftstoffe",
        merkmale="parfumfrei, sehr sanft, seifenfrei, für empfindliche Mischhaut",
        preis=2.95,
        beschreibung="Sehr mildes Waschgel für Mischhaut, die empfindlich reagiert oder schnell trocken wird. Reinigt ohne Duftstoffe und ist deshalb oft gut verträglich, selbst wenn die Haut schnell rötet. Ideal als unkomplizierte tägliche Reinigung für Gesicht und sensible Zonen.",
        inhaltsstoffe="Panthenol (beruhigt, fördert Regeneration), Glycerin (spendet Feuchtigkeit)",
        anwendung="Glycerin (Spendet Feuchtigkeit und verhindert Spannungsgefühle.) | Sehr milde Tenside (Reinigen die Haut besonders sanft, ohne sie zu reizen.) | Panthenol (Beruhigt die Haut und unterstützt die Regeneration.) | Ohne Duftstoffe, Alkohol und Farbstoffe (Minimiert das Risiko von Hautreizungen.) | Hautneutraler pH-Wert (Schützt die natürliche Hautbarriere.)",
        shop_link="https://www.dm.de/balea-med-ultra-sensitive-waschgel-p4058172920950.html",
        bild="Balea_Med_Ultra_Sensitive_Waschgel.png"
    )
    p26 = Produkt(
        name="Neutrogena Hydro Boost Reinigungsgel",
        bezeichnung="Feuchtigkeitsspendende Reinigung",
        merkmale="feuchtigkeitsspendend, leicht, erfrischend, für Mischhaut geeignet",
        preis=6.95,
        beschreibung="Feuchtigkeitsspendendes Reinigungsgel, das die Haut frisch und sauber macht, ohne nach dem Waschen zu spannen. Besonders angenehm, wenn du ein leichtes, geliges Hautgefühl magst und trotzdem Feuchtigkeit brauchst. Gut für Mischhaut, weil es reinigt, aber nicht unnötig austrocknet.",
        inhaltsstoffe="Hyaluronsäure (speichert Wasser, polstert Haut), Glycerin (verhindert Austrocknung)",
        anwendung="Täglich morgens und/oder abends auf feuchte Haut einmassieren und abspülen.",
        shop_link="https://www.dm.de/neutrogena-hydro-boost-reinigungsgel-p3574661389652.html | https://www.rossmann.de/de/pflege-und-duft-neutrogena-hydro-boost-reinigungsgel/p/3574661389652",
        bild="Neutrogena_Hydro_Boost.png"
    )
    p27 = Produkt(
        name="Eucerin DermatoCLEAN Reinigungsgel",
        bezeichnung="Mildes Gel für empfindliche Mischhaut",
        merkmale="mild, reizarm, feuchtigkeitsunterstützend, für sensible Mischhaut",
        preis=12.95,
        beschreibung="Mildes Reinigungsgel für empfindliche Mischhaut, das gründlich reinigt und die Haut gleichzeitig nicht aus dem Gleichgewicht bringt. Besonders gut geeignet, wenn du Reinigung willst, aber danach oft Trockenheit spürst. Hinterlässt ein sauberes, angenehmes Hautgefühl ohne starkes Entfetten.",
        inhaltsstoffe="APG-Komplex (besonders milde Tenside), Gluco-Glycerol (verbessert Feuchtigkeitsverteilung)",
        anwendung="Morgens & abends auf feuchte Haut auftragen, einmassieren und abspülen.",
        shop_link="https://www.dm.de/eucerin-dermatoclean-reinigungsgel-p4005800200131.html",
        bild="Eucerin_DermatoCLEAN_Reinigungsgel.png"
    )
    p28 = Produkt(
        name="CeraVe Feuchtigkeitslotion",
        bezeichnung="Leichte Pflege mit Barriereschutz",
        merkmale="leicht, barriere-stärkend, parfumfrei, für Mischhaut geeignet",
        preis=13.95,
        beschreibung="Leichte Feuchtigkeitslotion, die die Hautbarriere stärkt und gleichzeitig nicht zu schwer wirkt – gut für Mischhaut. Sie hydratisiert zuverlässig und hilft, trockene Partien zu beruhigen, ohne die T-Zone unnötig zu fetten. Ideal, wenn du eine ausgewogene „One-and-done“-Pflege suchst.",
        inhaltsstoffe="Ceramide (reparieren Schutzbarriere), Hyaluronsäure (hydratisiert)",
        anwendung="1–2× täglich auf die gereinigte Haut auftragen.",
        shop_link="https://www.dm.de/cerave-feuchtigkeitslotion-p3337875597418.html",
        bild="CeraVe_Feuchtigkeitslotion.png"
    )
    p29 = Produkt(
        name="La Roche-Posay Toleriane Fluid",
        bezeichnung="Minimalistische Pflege für Mischhaut",
        merkmale="minimalistisch, beruhigend, leicht, für sensible Haut",
        preis=16.95,
        beschreibung="Sehr leichtes Fluid für Mischhaut, das auf unnötige Reizstoffe verzichtet und die Haut beruhigt. Ideal, wenn du schnell auf Produkte reagierst oder Rötungen hast, aber trotzdem Feuchtigkeit brauchst. Hinterlässt ein angenehmes, gepflegtes Gefühl ohne schweren Film.",
        inhaltsstoffe="Glycerin (Feuchtigkeit), Thermalwasser (beruhigt sensible Haut)",
        anwendung="Morgens auf die gereinigte Haut auftragen.",
        shop_link="https://www.dm.de/la-roche-posay-toleriane-sensitive-fluid-p3337875735781.html",
        bild="Toleriane_Sensitive_Fluid.png"
    )
    p30 = Produkt(
        name="Balea Aqua Feuchtigkeitscreme",
        bezeichnung="Leichte Creme für Mischhaut",
        merkmale="leicht, erfrischend, feuchtigkeitsspendend, preiswert",
        preis=4.95,
        beschreibung="Leichte Feuchtigkeitscreme für Mischhaut, die schnell einzieht und die Haut frisch wirken lässt. Ideal, wenn du eine unkomplizierte Creme suchst, die nicht schwer ist, aber trotzdem Hydration liefert. Besonders angenehm im Alltag oder im Sommer, wenn reichhaltige Cremes zu viel sind.",
        inhaltsstoffe="Hyaluronsäure (hydratisiert), Algenextrakt (antioxidativ, feuchtigkeitsspendend)",
        anwendung="Täglich morgens und/oder abends anwenden.",
        shop_link="https://www.dm.de/balea-aqua-feuchtigkeitscreme-p4058172921864.html",
        bild="Balea_Gel_Aqua_Gesichtscreme.png"
    )
    p31 = Produkt(
        name="Vichy Aqualia Thermal Light",
        bezeichnung="Feuchtigkeitscreme für Mischhaut",
        merkmale="leicht, mineralreich, beruhigend, langanhaltend feucht",
        preis=19.95,
        beschreibung="Leichte Feuchtigkeitscreme für Mischhaut, die die Haut den Tag über angenehm hydratisiert. Sie eignet sich gut, wenn du Feuchtigkeit möchtest, aber keine fettige Textur verträgst. Hinterlässt ein glattes, frisches Hautgefühl und ist ideal als Tagespflege.",
        inhaltsstoffe="Hyaluronsäure (langanhaltende Feuchtigkeit), Thermalwasser (mineralreich, beruhigend)",
        anwendung="Morgens auf die gereinigte Haut auftragen.",
        shop_link="https://www.dm.de/vichy-aqualia-thermal-leichte-creme-p3337875597432.html",
        bild="Vichy_Aualia_Thermal_Feuchtigkeitspflege.png"
    )
    p32 = Produkt(
        name="La Roche-Posay Anthelios Invisible Fluid SPF50+",
        bezeichnung="Sehr leichtes Sonnenschutzfluid für Misch- & empfindliche Haut",
        merkmale="SPF50+, ultraleicht, kein Weißfilm, ideal unter Make-up",
        preis=18.95,
        beschreibung="Sehr leichtes Sonnenschutzfluid für Mischhaut und empfindliche Haut, das schnell einzieht und sich angenehm auf der Haut anfühlt. Es ist besonders beliebt, weil es wenig glänzt und meist keinen Weißfilm hinterlässt. Perfekt für den Alltag und als Make-up-Unterlage, wenn du Sonnenschutz nicht „spüren“ willst.",
        inhaltsstoffe="Mexoryl SX/XL (moderne UV-Filter, hoher UVA/UVB-Schutz), Glycerin (verhindert Austrocknung), Thermalwasser (beruhigt empfindliche Haut)",
        anwendung="Morgens als letzten Pflegeschritt großzügig auftragen, bei Sonne erneuern.",
        shop_link="https://www.dm.de/la-roche-posay-anthelios-invisible-fluid-spf50-p3337875730557.html | https://www.douglas.de/de/p/3001046915",
        bild="LaRochePosay_InvisibleFluid_50+.png"
    )
    p33 = Produkt(
        name="Eucerin Oil Control SPF50+",
        bezeichnung="Mattierender Sonnenschutz für Mischhaut",
        merkmale="SPF50+, mattierend, talgregulierend, sehr leicht",
        preis=17.95,
        beschreibung="Mattierender Sonnenschutz, der besonders gut für Mischhaut geeignet ist, weil er Glanz in der T-Zone reduzieren kann. Sehr angenehm, wenn du schnell fettig wirst, aber trotzdem hohen Schutz brauchst. Die Textur ist leicht und wird oft als sehr alltagstauglich beschrieben.",
        inhaltsstoffe="Carnitin (reguliert Talgproduktion), Licochalcone A (antioxidativ, entzündungshemmend), UV-Filter (UVA/UVB-Schutz)",
        anwendung="Morgens großzügig auftragen, bei Sonne regelmäßig nachlegen.",
        shop_link="https://www.dm.de/eucerin-oil-control-spf50-p4005800301646.html",
        bild="Eucerin_Oil_Control_SunGel-Creme_50+.png"
    )
    p34 = Produkt(
        name="Nivea UV Gesicht Mattierend SPF50",
        bezeichnung="Mattierender Sonnenschutz für Mischhaut",
        merkmale="SPF50, mattierendes Finish, alltagstauglich, gut verträglich",
        preis=8.95,
        beschreibung="Mattierender Sonnenschutz für Mischhaut, der im Alltag helfen kann, Glanz zu reduzieren und trotzdem hohen Schutz zu liefern. Gut, wenn du eine günstige Option suchst, die nicht stark brennt und sich angenehm tragen lässt. Je nach Haut kann er etwas reichhaltiger wirken, ist aber insgesamt sehr praktikabel.",
        inhaltsstoffe="Vitamin E (Antioxidans gegen UV-Stress), UV-Filter (Sonnenschutz)",
        anwendung="Morgens großzügig auftragen, bei Sonne nachlegen.",
        shop_link="https://www.dm.de/nivea-uv-gesicht-mattierend-spf50-p4005900463118.html | https://www.rossmann.de/de/pflege-und-duft-nivea-sun-uv-gesicht-mattierend-spf50/p/4005900463118",
        bild="NIVEA_SUN_Gesichtsschutz.png"
    )
    p35 = Produkt(
        name="Vichy Capital Soleil UV-Clear SPF50+",
        bezeichnung="Sonnenschutz bei Mischhaut & Unreinheiten",
        merkmale="SPF50+, für Unreinheiten, talgausgleichend, sehr leicht",
        preis=19.95,
        beschreibung="Sonnenschutz speziell für Mischhaut, die zu Unreinheiten und verstopften Poren neigt. Die Formulierung setzt auf ausgleichende Wirkstoffe, damit die Haut weniger glänzt und sich trotzdem geschützt anfühlt. Ideal, wenn du SPF willst, ohne Angst vor „Pickel durch Sonnencreme“.",
        inhaltsstoffe="Niacinamid (reguliert Talg, beruhigt), Salicylsäure (wirkt gegen verstopfte Poren), UV-Filter (Sonnenschutz)",
        anwendung="Morgens auftragen, bei Sonne regelmäßig erneuern.",
        shop_link="https://www.dm.de/vichy-capital-soleil-uv-clear-spf50-p3337875860629.html",
        bild="Vichy_Capital_Soleil_50+.png"
    )
    p36 = Produkt(
        name="Balea Niacinamide Serum",
        bezeichnung="Ausgleichendes Serum für Mischhaut",
        merkmale="talgregulierend, porenverfeinernd, preiswert, leicht",
        preis=4.95,
        beschreibung="Ausgleichendes Serum für Mischhaut, das besonders in der T-Zone helfen kann, Glanz zu reduzieren und das Hautbild ebenmäßiger wirken zu lassen. Gut geeignet, wenn du sichtbare Poren hast oder zu kleinen Unreinheiten neigst. Die leichte Textur lässt sich sehr gut unter Creme oder SPF schichten.",
        inhaltsstoffe="Niacinamid 10% (verfeinert Poren, reguliert Talg), Zink (antibakteriell, talgregulierend)",
        anwendung="Nach der Reinigung auftragen, danach Creme/SPF verwenden.",
        shop_link="https://www.dm.de/balea-niacinamide-serum-p4058172776518.html",
        bild="Balea_Niacinamide_Serum.png"
    )
    p37 = Produkt(
        name="La Roche-Posay Niacinamide 10 Serum",
        bezeichnung="Ausgleichendes Serum bei Unreinheiten",
        merkmale="porenverfeinernd, talgausgleichend, beruhigend",
        preis=34.95,
        beschreibung="Ausgleichendes Serum für Mischhaut, besonders wenn du zu Unreinheiten, Rötungen oder unruhiger Textur neigst. Niacinamid kann helfen, das Hautbild zu glätten und die Talgproduktion zu regulieren. Ideal als Abendserum, wenn du gezielt an Poren und Hautbalance arbeiten willst.",
        inhaltsstoffe="Niacinamid (Poren & Rötungen, Talgregulation), Hyaluronsäure (Feuchtigkeit)",
        anwendung="Abends nach der Reinigung auftragen.",
        shop_link="https://www.dm.de/la-roche-posay-niacinamide-10-serum-p3337875861091.html",
        bild="LaRochePosay_Niacinamide10Serum.png"
    )
    p38 = Produkt(
        name="Geek & Gorgeous B-Bomb",
        bezeichnung="Leichtes Niacinamid-Serum",
        merkmale="talgkontrollierend, leicht, porenfreundlich, für Mischhaut",
        preis=10.95,
        beschreibung="Leichtes Niacinamid-Serum, das speziell für ein ausgeglicheneres Hautbild bei Mischhaut entwickelt ist. Gut geeignet, wenn du Glanz reduzieren möchtest, aber keine schweren Texturen verträgst. Lässt sich einfach in fast jede Routine integrieren und ist angenehm unter Creme oder SPF.",
        inhaltsstoffe="Niacinamid 10% (Hautbildverbesserung, Talgregulation), Zink PCA (Talgkontrolle, antibakteriell)",
        anwendung="Täglich nach der Reinigung anwenden.",
        shop_link="https://geekandgorgeous.com/products/b-bomb",
        bild="GeekandGorgeous_BBomb_Serum.png"
    )
    p39 = Produkt(
        name="Balea Beauty Expert Peeling Toner",
        bezeichnung="Mildes chemisches Peeling",
        merkmale="einsteigerfreundlich, glättend, mild, preiswert",
        preis=4.95,
        beschreibung="Mildes Peeling-Toner-Produkt für Mischhaut, das die Hautoberfläche glätten und den Teint frischer wirken lassen kann. Durch die Kombination aus AHA und PHA ist es oft sanfter als sehr starke Peelings. Ideal als Einstieg, wenn du Peeling testen möchtest, ohne direkt ein „hartes“ Produkt zu nehmen.",
        inhaltsstoffe="AHA (glättet Hautoberfläche), PHA (sehr mild, feuchtigkeitsspendend)",
        anwendung="Abends anwenden, langsam starten und nicht täglich übertreiben.",
        shop_link="https://www.dm.de/balea-beauty-expert-aha-pha-peeling-toner-p4058172776556.html",
        bild="Balea_Liquid_Peeling.png"
    )

    db.session.add_all([
        p1, p2, p3, p4, p5, p6, p7, p8, p9, p10, p11, p12, p13, p14, p15, p16, p17, p18, p19, p20, p21, p22, p23,
        p24, p25, p26, p27, p28, p29, p30, p31, p32, p33, p34, p35, p36, p37, p38, p39
    ])
    db.session.commit()


    # Benutzer 
    u1 = Benutzer(
        passwort_hash="$2b$12$Vy1c9c.ptQxMHqgegATtOe8oBXeYZxdNggUPIghLHGTrF9/XiY/We", #Passwort!1
        name="Marie Weber",
        email="marie.wbr@gmail.com",
        hauttyp_id=1
    )

    u2 = Benutzer(
        passwort_hash="$2b$12$VYU/RFDF/otilLu6zP/b1eOjH8ahgsUZ8ivEfKxBaQ67JKBtfqLVG", #Passwort!2
        name="Lina Kaufmann",
        email="lina.kfm@gmail.com",
        hauttyp_id=1
    )

    u3 = Benutzer(
        passwort_hash="$2b$12$xt1/cAQ9qoFHUgeAa0DZ8eDBJCoBh.c9bxL7emFD4pvJE3scDGfGm", #Passwort!3
        name="Lukas Müller",
        email="lukas.mlr@gmail.com",
        hauttyp_id=2
    )

    db.session.add_all([u1, u2, u3])
    db.session.commit()
  
   
    # Bewertungen 
    b1 = Bewertung(
        produkt_id=1,
        benutzer_id=2,
        sterne=4,
        kommentar="sehr gutes Produkt"
    )
    b2 = Bewertung(
        produkt_id=1,
        benutzer_id=3,
        sterne=5,
        kommentar="Perfekt für trockene Haut"
    )
    b3 = Bewertung(
        produkt_id=6,
        benutzer_id=2,
        sterne=5,
        kommentar="spendet sehr viel Feuchtigkeit"
    )

    db.session.add_all([b1, b2, b3])
    db.session.commit()
    

    # Favoriten 
    # Benutzer 2 favorisiert Produkte
    u2.favoriten.append(p1)
    u2.favoriten.append(p2)
    u2.favoriten.append(p6)
    u2.favoriten.append(p9)
    u2.favoriten.append(p10)
    u2.favoriten.append(p13)
    u2.favoriten.append(p15)

    # Benutzer 3 favorisiert Produkte
    u3.favoriten.append(p25)
    u3.favoriten.append(p30)

    db.session.commit()
 

    # Kategorien ↔ Produkte (GEHÖRT_ZU) 
   
    # Reinigung (Kategorie 1)
    k1.produkte.append(p1)
    k1.produkte.append(p2)
    k1.produkte.append(p3)
    k1.produkte.append(p4)
    k1.produkte.append(p5)
    k1.produkte.append(p24)
    k1.produkte.append(p25)
    k1.produkte.append(p26)
    k1.produkte.append(p27)

    # Feuchtigkeitscreme (Kategorie 2)
    k2.produkte.append(p6)
    k2.produkte.append(p7)
    k2.produkte.append(p8)
    k2.produkte.append(p9)
    k2.produkte.append(p10)
    k2.produkte.append(p28)
    k2.produkte.append(p29)
    k2.produkte.append(p30)
    k2.produkte.append(p31)

    # Sonnencreme (Kategorie 3)
    k3.produkte.append(p11)
    k3.produkte.append(p12)
    k3.produkte.append(p13)
    k3.produkte.append(p14)
    k3.produkte.append(p32)
    k3.produkte.append(p33)
    k3.produkte.append(p34)
    k3.produkte.append(p35)

    # Serum / Booster (Kategorie 4)
    k4.produkte.append(p15)
    k4.produkte.append(p16)
    k4.produkte.append(p17)
    k4.produkte.append(p18)
    k4.produkte.append(p36)
    k4.produkte.append(p37)
    k4.produkte.append(p38)

    # Peeling (Kategorie 5)
    k5.produkte.append(p19)
    k5.produkte.append(p20)
    k5.produkte.append(p21)
    k5.produkte.append(p22)
    k5.produkte.append(p23)
    k5.produkte.append(p39)

    db.session.commit()


    # Produkt ↔ Hauttyp (GEEIGNET) – nur append()

    # trocken (hauttyp 1)
    ht1.produkte_geeignet.append(p1)
    ht1.produkte_geeignet.append(p2)
    ht1.produkte_geeignet.append(p3)
    ht1.produkte_geeignet.append(p4)
    ht1.produkte_geeignet.append(p5)
    ht1.produkte_geeignet.append(p6)
    ht1.produkte_geeignet.append(p7)
    ht1.produkte_geeignet.append(p8)
    ht1.produkte_geeignet.append(p9)
    ht1.produkte_geeignet.append(p10)
    ht1.produkte_geeignet.append(p11)
    ht1.produkte_geeignet.append(p12)
    ht1.produkte_geeignet.append(p13)
    ht1.produkte_geeignet.append(p14)
    ht1.produkte_geeignet.append(p15)
    ht1.produkte_geeignet.append(p16)
    ht1.produkte_geeignet.append(p17)
    ht1.produkte_geeignet.append(p18)
    ht1.produkte_geeignet.append(p19)
    ht1.produkte_geeignet.append(p20)
    ht1.produkte_geeignet.append(p21)
    ht1.produkte_geeignet.append(p22)
    ht1.produkte_geeignet.append(p23)

    # mischhaut (hauttyp 2)
    ht2.produkte_geeignet.append(p15)
    ht2.produkte_geeignet.append(p16)
    ht2.produkte_geeignet.append(p19)
    ht2.produkte_geeignet.append(p24)
    ht2.produkte_geeignet.append(p25)
    ht2.produkte_geeignet.append(p26)
    ht2.produkte_geeignet.append(p27)
    ht2.produkte_geeignet.append(p28)
    ht2.produkte_geeignet.append(p29)
    ht2.produkte_geeignet.append(p30)
    ht2.produkte_geeignet.append(p31)
    ht2.produkte_geeignet.append(p32)
    ht2.produkte_geeignet.append(p33)
    ht2.produkte_geeignet.append(p34)
    ht2.produkte_geeignet.append(p35)
    ht2.produkte_geeignet.append(p36)
    ht2.produkte_geeignet.append(p37)
    ht2.produkte_geeignet.append(p38)
    ht2.produkte_geeignet.append(p39)

    # ölig (hauttyp 3)
    ht3.produkte_geeignet.append(p2)
    ht3.produkte_geeignet.append(p16)
    ht3.produkte_geeignet.append(p17)
    ht3.produkte_geeignet.append(p21)
    ht3.produkte_geeignet.append(p28)
    ht3.produkte_geeignet.append(p32)
    ht3.produkte_geeignet.append(p33)
    ht3.produkte_geeignet.append(p38)

    # sensibel (hauttyp 4)
    ht4.produkte_geeignet.append(p1)
    ht4.produkte_geeignet.append(p2)
    ht4.produkte_geeignet.append(p3)
    ht4.produkte_geeignet.append(p6)
    ht4.produkte_geeignet.append(p12)
    ht4.produkte_geeignet.append(p16)
    ht4.produkte_geeignet.append(p17)
    ht4.produkte_geeignet.append(p20)
    ht4.produkte_geeignet.append(p21)
    ht4.produkte_geeignet.append(p25)

    # normal (hauttyp 5)
    ht5.produkte_geeignet.append(p1)
    ht5.produkte_geeignet.append(p6)
    ht5.produkte_geeignet.append(p11)
    ht5.produkte_geeignet.append(p12)
    ht5.produkte_geeignet.append(p15)
    ht5.produkte_geeignet.append(p16)
    ht5.produkte_geeignet.append(p19)
    ht5.produkte_geeignet.append(p21)
    ht5.produkte_geeignet.append(p24)
    ht5.produkte_geeignet.append(p28)

    db.session.commit()



