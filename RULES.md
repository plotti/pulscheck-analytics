# PulsCheck – Agentenregeln

> Kanonische Geschäftslogik für den nao Analytics Agent.
> Jede Änderung wird via Pull Request reviewt und mit
> entsprechenden Tests in `tests/` abgedeckt.

## Sprache und Zeitzone

- Antworten standardmässig auf Deutsch (Sie-Form), ausser explizit anders gefragt.
- Alle Datums- und Zeitangaben in **Europe/Zurich**, sofern nicht anders spezifiziert.
- "Letzter Monat" bedeutet der vorangegangene Kalendermonat in Europe/Zurich,
  vom 1. bis zum letzten Tag, 00:00 bis 23:59:59.
- Quartalsdefinition: Q1 = Januar bis März, Q2 = April bis Juni, Q3 = Juli bis September, Q4 = Oktober bis Dezember.
- Runde alle Antworten immer auf eine Nachkommastelle.

## Währungen und Steuern

- Alle Geldbeträge in CHF, **brutto** inkl. 8.1 % Schweizer MwSt,
  ausser ein Bericht erfordert explizit netto.
- Wenn netto verlangt: `amount_chf - vat_chf`.

## Metrik: MRR (Monthly Recurring Revenue)

- Definition: Summe der `monthly_price_chf` aller `subscriptions`,
  bei denen `started_at <= Stichtag` UND
  `(canceled_at IS NULL OR canceled_at > Stichtag)`.
- MRR enthält **ausschliesslich Subscription-Umsatz**.
- **Paket-Umsatz wird NIEMALS in MRR verrechnet**.
- Bei Stichtag ohne Uhrzeit: 23:59:59 Europe/Zurich des Stichtags.
- Gepauste Subscriptions (`current_plan = 'subscription_paused'`) zählen
  weiterhin in MRR, solange `canceled_at IS NULL`.

## Metrik: Paket-Umsatz (Response Packages) – Single Source of Truth

- Die **EINZIGE autoritative Quelle** für Paket-Umsatz ist
  `response_packages.price_chf` (gefiltert nach `purchased_at`).
- `invoices` mit `invoice_type = 'response_package'` sind die
  Abrechnungssicht der gleichen Käufe und dürfen **NIEMALS additiv**
  zu `response_packages` verwendet werden.
- Für Cashflow-Sicht (bezahlt vs. offen) wird `invoices` verwendet,
  aber dann **ohne** `response_packages`.
- Refunds (`invoices.status = 'refunded'` UND `invoice_type = 'response_package'`)
  werden abgezogen, wenn der Refund-Zeitraum mit der Frage übereinstimmt.

## Metrik: Aktive Kund:in

- Standard-Definition für Berichte: `current_plan = 'subscription_active'` ZUM Stichtag.
- Wenn die Frage explizit Nutzung erwähnt: zusätzlich
  - mindestens eine veröffentlichte Befragung (`surveys.status IN ('active','closed')`)
    ODER
  - mindestens ein Paketkauf in den letzten 30 Tagen.
- Bei Mehrdeutigkeit: rückfragen, welche Definition gewünscht ist.

## Metrik: Aktive Subscription "im Zeitraum"

- Wenn die Frage einen Zeitraum nennt (z. B. "im April"), bezieht sich
  "aktive Subscription" auf Kund:innen mit:
  - `started_at < Zeitraum-Beginn`
  - UND `(canceled_at IS NULL OR canceled_at > Zeitraum-Ende)`.
- Also: Kund:innen, die den **GANZEN** Zeitraum aktiv waren.
- Wenn die Frage einen Stichtag nennt: Aktivität zum Stichtag.

## Metrik: Churn (im Zeitraum)

- Definition: Anzahl `subscriptions` mit `canceled_at` IM Zeitraum
  UND `started_at < Zeitraum-Beginn` (also: war zu Beginn des Zeitraums aktiv).
- Trial-Kund:innen (`current_plan = 'free'` ohne Subscription) werden
  **NICHT** als Churn gezählt.

## Metrik: Befragungs-Antworten

- "Antworten" bedeutet standardmässig `is_complete = 1` in `survey_responses`.
- Unvollständige Antworten (`is_complete = 0`) **NUR** auf explizite Nachfrage.
- Eine Antwort wird gegen das zum Zeitpunkt aktive Paket des:der
  Survey-Eigentümer:in gerechnet (FIFO über `response_packages`).

## Tabellen-Hinweise

- `invoices.invoice_type` unterscheidet `'subscription'` (monatliche Rechnung)
  von `'response_package'` (Paketkauf). Niemals zusammenwerfen, ohne
  explizit zu summieren.
- `response_packages.responses_used` != `survey_responses`-Count: ersteres
  ist die Abrechnungssicht, letzteres die Event-Sicht. Können kurzfristig
  divergieren.
- `surveys.language` ist die Befragungssprache; `survey_responses.respondent_country`
  ist das Land der Befragten und kann von der Sprache abweichen.

## Verhaltensregeln

- Bei jeder Antwort: SQL-Query und ungefähren Zeilenumfang nennen.
- Bei Beträgen unter 100 CHF Zweifel an Plausibilität aussprechen.
- Wenn eine Frage nur mit erheblicher Annahme beantwortbar ist:
  zuerst rückfragen.
- Forecasts ohne hinterlegtes statistisches Modell: Antwort explizit
  als **Schätzung** kennzeichnen.
- Niemals Daten erfinden, wenn die Tabelle leer ist – stattdessen: "Keine Daten gefunden".
