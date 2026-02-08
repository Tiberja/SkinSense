---
title: Referenz
parent: Technische-Doku
nav_order: 3
---

{: .label }
[Tiberja Gündüz]

{: .no_toc }
# Referenzdokumentation

<details open markdown="block">
{: .text-delta }
<summary>Inhaltsverzeichnis</summary>
+ ToC
{: toc }
</details>

## Authentifizierung

### `login()`

**Route:** `/login`

**Methode:** `GET` `POST` 

**Zweck:** Zeigt die Login-Seite an und authentifiziert den Benutzer anhand ihrer Zugangsdaten.

**Ausgabe:**

![login() sample](../assets/images/login.png)

---

### `register()`

**Route:** `/register`

**Methode:** `GET` `POST` 

**Zweck:** Ermöglicht neuen Benutzern die Registrierung eines Accounts.

**Ausgabe:**

![register() sample](../assets/images/register.png)

---

### `logout()`

**Route:** `/logout`

**Methode:** `GET` 

**Zweck:** Meldet den aktuellen Benutzer ab und beendet die Session.

**Ausgabe:**

Benutzer wird zur Startseite weitergeleitet.

---

## Benutzerseiten

### `index()`

**Route:** `/`

**Methode:** `GET`

**Zweck:** Zeigt die Startseite der Website an und dient als Einstiegspunkt für Benutzer. 

**Ausgabe:**

![index() sample](../assets/images/home.png)

---

### `skin_type()`

**Route:** `/skin_type`

**Methode:** `GET` `POST`

**Zweck:** Ermöglicht die Auswahl eines Hauttyps, um passende Produkte zu erhalten. 

**Ausgabe:**

![skin_type() sample](../assets/images/skin_type.png)

---

### `products()`

**Route:** `/products`

**Methode:** `GET` 

**Zweck:** Zeigt eine Liste von Produkten, basierend auf dem ausgewählten Hauttyp.

**Ausgabe:**

![products() sample](../assets/images/products.png)

---

### `product_details()`

**Route:** `/product_details/<int:product_id>`

**Methode:** `GET` 

**Zweck:** Zeigt Detailinformationen zu einem ausgewählten Produkt, inklusive Bewertungen.

**Ausgabe:**

![product_details() sample](../assets/images/product_details.png)

---

### `favorites()`

**Route:** `/favorites`

**Methode:** `GET` 

**Zweck:** Zeigt eine Übersicht aller vom Benutzer favorisierten Produkte.

**Ausgabe:**

![favorites() sample](../assets/images/favoriten.png)

---

## Benutzerinteraktionen

### `toggle_favorite(product_id)`

**Route:** `/favorites/toggle/<int:product_id>`

**Methode:** `POST` 

**Zweck:** Fügt ein Produkt zur Favoritenliste hinzu oder entfernt es davon. 

**Ausgabe:**
Das Herz wird ausgefüllt und das jeweilige Produkt wird in der Favoritenliste angezeigt. 


---

### `add_review(product_id)`

**Route:** `/products/<int:product_id>/reviews`

**Methode:** `POST` 

**Zweck:** Ermöglicht Benutzern eine Bewertung zu einem Produkt hinzuzufügen. 

**Ausgabe:**

![add_review(product_id) sample](../assets/images/bewertungen.png)

---

### `delete_review(product_id, review_id)`

**Route:** `/products/<int:product_id>/reviews/<int:review_id>/delete`

**Methode:** `POST` 

**Zweck:** Ermöglicht Benutzern ihre eigene Bewertung wieder zu löschen. 

**Ausgabe:**

Die ausgewählte Bewertung wird gelöscht und die Seite aktualisiert sich. 

---

## Beispieldaten einfügen

### `run_insert_sample()`

**Route:** `/insert/sample`

**Methode:** `GET`

**Zweck:** Leert die Datenbank und fügt Beispieldaten hinzu. 

**Ausgabe:**

Browser zeigt: `Database flushed and populated with some sample data.`
