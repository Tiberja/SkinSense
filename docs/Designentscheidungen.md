---
title: Design Decisions
nav_order: 3
---

{: .label }
[Tiberja Gündüz]

{: .no_toc }
# Designentscheidungen

<details open markdown="block">
{: .text-delta }
<summary>Inhaltsverzeichnis</summary>
+ ToC
{: toc }
</details>

## 01: Einsatz von SQLAlchemy als ORM

### Metadaten

Status
: In Bearbeitung - **Entschieden** - Veraltet

Aktualisiert am
: 07.02.2026

### Problemstellung

Sollten Datenbankoperationen (create, read, update, delete) durch direkte SQL-Abfragen umgesetzt werden oder durch den Einsatz von SQLAlchemy als Object-Relational Mapper (ORM)?

Die Webanwendung ist in Python mit Flask umgesetzt und verwendet eine relationale Datenbank. Für den Projektumfang wäre sowohl die Nutzung von direktem SQL als auch ORM grundsätzlich ausreichend. 

Da sich die Anwendung jedoch weiterentwickeln kann, ist davon auszugehen, dass sich das Datenbankschema im Laufe der Entwicklung mehrfach ändert und die Datenbankstruktur mit zunehmender Funktionalität komplexer wird.

### Entscheidung

Wir haben uns entschieden, SQLAlchemy als ORM für alle Datenbankoperationen einzusetzen. 

SQLAlchemy ermöglicht es, Datenmodelle und deren Beziehungen klar zu definieren und Datenbankzugriffe einheitlich umzusetzen. Dadurch bleibt der Code übersichtlich und leicht wartbar, insbesondere bei Änderungen am Datenbankschema. 

*Entschieden von:* github.com/tiberja, github.com/Acelya

### Betrachtete Alternativen

Wir haben zwei Alternativen betrachtet:

+ Direkte SQL-Abfragen
+ SQLAlchemy (ORM)

| Kriterium | Direkte SQL-Abfragen | SQLAlchemy |
| --- | --- | --- |
| **Know-how** | ✔️ Grundkenntnisse vorhanden | ❌ Einarbeitung in ORM notwendig |
| **Wartbarkeit** | ❌ SQL an vielen Stellen im Code | ✔️ Zentrale Modellstruktur |
| **Schema-Änderung** | ❌ Aufwendig bei vielen Queries | ✔️ Änderungen an Modellen möglich |
| **Lesbarkeit** | ❌ Schnell unübersichtlich | ✔️ Klare Objektstruktur |
| **Fehleranfälligkeit** | ❌ Höheres Risiko durch manuelle SQL-Abfragen| ✔️ Reduziert durch strukturierte Modelle |

---

## 02: Verzicht auf UI-Frameworks wie Bootstrap

### Metadaten

Status
: In Bearbeitung - **Entschieden** - Veraltet

Aktualisiert am
: 07.02.2026

### Problemstellung

Für die Benutzeroberfläche der Anwendung musste entschieden werden, ob ein bestehendes UI-Framework wie Bootstrap eingesetzt werden soll oder ob das Layout mit eigenem HTML und CSS umgesetzt wird. 

Beide Ansätze waren grundsätzlich geeignet, um die benötigten Seiten der Anwendung darzustellen. Mit zunehmender Komplexität der Benutzeroberfläche hätte ein Framework jedoch stärkeren Einfluss auf Struktur und Gestaltung. 

### Entscheidung

Wir haben uns entschieden, auf den Einsatz von UI-Frameworks wie Bootstrap zu verzichten und das User Interface ausschließlich mit eigenem HTML und CSS umzusetzen. 

Dadurch konnte das Design gezielt an die Anforderungen der Anwendung angepasst werden, ohne von vordefinierten Komponenten oder Layoutvorgaben abhängig zu sein. 

*Entschieden von:* github.com/tiberja, github.com/Acelya

### Betrachtete Alternativen

Wir haben zwei Alternativen betrachtet:

+ Einsatz eines UI-Frameworks (z.B Bootstrap)
+ Eigenes HTML- und CSS-Design
  
| Kriterium | UI-Framework | Eigenes HTML & CSS |
| --- | --- | --- |
| **Einrichtungsaufwand** | ✔️ Schneller Einstieg | ❌ Höherer Initialaufwand |
| **Gestaltungsfreiheit** | ❌ Stark vorgegeben | ✔️ Volle Kontrolle |
| **Abhängigkeiten** | ❌ Externe Bibliothek | ✔️ Keine externen UI-Abhängigkeiten |
| **Anpassbarkeit** | ❌ Anpassungen oft umständlich | ✔️ Direkt anpassbar |
| **Lernfaktor** | ❌ Abstraktion vieler Grundlagen| ✔️ Besseres Verständnis von HTML/CSS |

---

## 03: Sessionbasierte Authentifizierung zur Benutzerverwaltung

### Metadaten

Status
: In Bearbeitung - **Entschieden** - Veraltet

Aktualisiert am
: 07.02.2026

### Problemstellung

Die Anwendung benötigt eine Möglichkeit, Benutzer eindeutig zu identifizieren und benutzerspezifische Funktionen wie Favoriten und Bewertungen nur für angemeldete Benutzer zugänglich zu machen.

Dabei musste entschieden werden, wie der Authentifizierungszustand eines Benutzers über mehrere Seitenaufrufe hinweg verwaltet wird. 

### Entscheidung

Wir haben uns für eine sessionbasierte Authentifizierung entschieden. Nach erfolgreichem Login wird der Benutzer über eine serverseitige Session identifiziert, die bei weiteren Anfragen zur Zugriffskontrolle verwendet wird.  

*Entschieden von:* github.com/tiberja, github.com/Acelya

### Betrachtete Alternativen

Wir haben zwei Alternativen betrachtet:

+ Sessionbasierte Authentifizierung 
+ Tokenbasierte Authentifizierung

| Kriterium | Tokenbasierte Authentifizierung | Sessionbasierte Authentifizierung |
| --- | --- | --- |
| **Komplexität** | ❌ Höherer Implementierungsaufwand | ✔️ Einfach umzusetzen |
| **Zustandsverwaltung** | ❌ Manuelle Token-Verwaltung | ✔️ Automatische Session-Verwaltung |
| **Sicherheit** | ✔️ Sicher bei korrekter Umsetzung | ✔️ Sicher bei korrekter Implementierung |
| **Wartbarkeit** | ❌ Mehr Logik notwendig | ✔️ Übersichtlich |

---
