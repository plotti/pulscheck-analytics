# PulsCheck – Datenmodell

> Diese Datei beschreibt die operativen Tabellen in menschenlesbarer Form.
> Sie wird vom nao-Agenten als zusätzlicher Context geladen.

## Geschäftsmodell in einem Satz

Schweizer Online-Befragungs-SaaS (vergleichbar SurveyMonkey) mit
hybridem Modell: monatliches Subscription-Abo (19.99 CHF) für den
Survey-Editor plus Pay-per-Use-Pakete (S/M/XL) für die effektive
Datenerhebung.

## Tabellen

### `customers` – Stammdaten

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | Primary Key |
| `email` | TEXT | unique |
| `signup_date` | DATE | Registrierungsdatum |
| `country` | TEXT | ISO-2-Code (CH, DE, AT, FR, IT, GB) |
| `current_plan` | TEXT | `subscription_active`, `subscription_paused`, `free`, `churned` |
| `marketing_consent` | BOOL | Opt-in für Marketing-Mails |

### `subscriptions` – Abo-Historie

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | |
| `customer_id` | FK | Verweis auf `customers.id` |
| `started_at` | TIMESTAMP | mit Europe/Zurich-Offset |
| `canceled_at` | TIMESTAMP | NULL = aktiv |
| `monthly_price_chf` | NUMERIC | aktuell durchgängig 19.99 |

Eine Kund:in kann mehrere historische Subscriptions haben (Re-Activation).

### `invoices` – Abrechnungen

Sowohl Subscription-Rechnungen als auch Paketkauf-Rechnungen landen in dieser Tabelle.

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | |
| `customer_id` | FK | |
| `amount_chf` | NUMERIC | brutto inkl. 8.1 % MwSt |
| `vat_chf` | NUMERIC | enthaltener MwSt-Anteil |
| `invoice_type` | TEXT | `subscription` ODER `response_package` |
| `status` | TEXT | `paid` (95–96 %), `failed` (3–4 %), `refunded` (~1 %) |
| `invoiced_at` | TIMESTAMP | |

**Wichtig:** Für Paket-Umsatz ist `response_packages` die Single Source of Truth,
nicht `invoices`. Siehe `RULES.md`.

### `response_packages` – Pay-per-Use-Paketkäufe

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | |
| `customer_id` | FK | |
| `package_size` | TEXT | `S`, `M` oder `XL` |
| `price_chf` | NUMERIC | 9 (S), 19 (M), 29 (XL) |
| `responses_included` | INT | 5'000 (S), 10'000 (M), 100'000 (XL) |
| `responses_used` | INT | bereits verbrauchte Antworten aus diesem Paket |
| `purchased_at` | TIMESTAMP | |

### `surveys` – erstellte Befragungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | |
| `customer_id` | FK | Eigentümer:in der Befragung |
| `title` | TEXT | freier Text |
| `language` | TEXT | `de`, `fr`, `it`, `en` |
| `status` | TEXT | `draft`, `active`, `closed` |
| `created_at` | TIMESTAMP | |
| `closed_at` | TIMESTAMP | NULL bei `draft` und `active` |

### `survey_responses` – einzelne ausgefüllte Befragungen

| Spalte | Typ | Beschreibung |
|---|---|---|
| `id` | UUID | |
| `survey_id` | FK | Verweis auf `surveys.id` |
| `completed_at` | TIMESTAMP | |
| `response_duration_seconds` | INT | Dauer der Beantwortung |
| `respondent_country` | TEXT | ISO-2-Code des:der Antwortenden |
| `is_complete` | BOOL | nur `1` zählt fürs Paketkontingent |

## Beziehungsgraph

```
customers ────┬──< subscriptions
              ├──< invoices
              ├──< response_packages
              └──< surveys ──< survey_responses
```

## Wichtige Konventionen

- **Zeitzone:** Alle Zeitstempel sind als String mit Europe/Zurich-Offset
  gespeichert (Sommer +02:00, Winter +01:00).
- **Währung:** Alle Beträge in CHF, brutto inkl. 8.1 % MwSt.
- **Pakete und Verbrauch:** Eine Antwort verbraucht das aktive Paket
  des:der Survey-Eigentümer:in (FIFO). `responses_used` und gezählte
  Antworten in `survey_responses` können kurzfristig divergieren.
