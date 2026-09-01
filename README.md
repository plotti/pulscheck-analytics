# PulsCheck Analytics – nao Demo Project

Dies ist das vollständige Begleitprojekt zum Blogbeitrag **„Agentic BI für KMU
in der Praxis: Ein Schweizer SaaS-Fall mit nao"**.

Es enthält alles, was nötig ist, um den im Beitrag beschriebenen Aufbau
selbst zu reproduzieren:

- vollständiges SQL-Schema (`schema.sql`)
- deterministisches Seed-Skript (`seed.py`) mit über 280'000 realistischen Datensätzen
- nao-Konfiguration (`nao_config.yaml`)
- kanonische Geschäftsregeln (`RULES.md`)
- vier YAML-Tests (`tests/`)
- Beispielqueries für den Agenten (`queries/`)
- lokaler Test-Runner (`run_tests.py`) als Pendant zu `nao test`

## Quick Start

```bash
# 1. DuckDB installieren
pip install duckdb

# 2. Datenbank seeden (deterministisch, Seed=42)
#    Alternativ: fertige Demo-DB liegt im Repo (pulscheck.duckdb) → Schritt optional
python seed.py

# 3. Tests gegen die DB validieren (ohne LLM)
pip install pyyaml
python run_tests.py
```

Erwarteter Output: `4/4 passed`.

## Projektstruktur

```
pulscheck-analytics/
├── README.md
├── schema.sql                     # DuckDB-Schema, 6 Tabellen
├── seed.py                        # Generator für 280k+ Zeilen
├── verify_tests.py                # Verifikationsskript für Erwartungswerte
├── run_tests.py                   # Lokaler Test-Runner (nao-test-Pendant)
├── pulscheck.duckdb               # Fertige Demo-DB (im Repo, via seed.py reproduzierbar)
├── nao_config.yaml                # nao-Konfiguration
├── RULES.md                       # Kanonische Geschäftsregeln (MECE)
├── tests/
│   ├── mrr_end_of_april.yml
│   ├── churn_april.yml
│   ├── package_revenue_q1.yml
│   └── dormant_subscribers.yml
├── queries/
│   ├── mrr_at_date.sql
│   └── dormant_subscribers.sql
├── docs/
│   └── data_model.md              # menschenlesbare Schema-Doku
└── agent/
    ├── mcps/
    └── skills/
```

## Datenmodell

| Tabelle | Zweck | Zeilen (Seed) |
|---|---|---|
| `customers` | Stammdaten | 4'200 |
| `subscriptions` | Abo-Historie (active/paused/churned) | ca. 3'600 |
| `invoices` | Abrechnung (subscription + response_package) | ca. 55'000 |
| `response_packages` | Pay-per-Use-Paketkäufe (S/M/XL) | ca. 7'500 |
| `surveys` | erstellte Befragungen (de/fr/it/en) | ca. 6'300 |
| `survey_responses` | einzelne ausgefüllte Befragungen | ca. 206'000 |

Vollständige Spaltenbeschreibungen siehe [`docs/data_model.md`](docs/data_model.md).

## Erwartete Test-Ergebnisse (Seed=42, Stichtag = 2026-04-30)

| Test | Erwartet |
|---|---|
| `mrr_end_of_april` | MRR = 57'331.32 CHF, 2'868 aktive Subscriptions |
| `churn_april` | 108 gechurnte Kund:innen, 2'158.92 CHF verlorener MRR |
| `package_revenue_q1` | Sieger: M (13'699 CHF, 43.6 %), gefolgt von XL (29.1 %), S (27.3 %) |
| `dormant_subscribers` | 2'229 durchgehend aktive Sub-Kund:innen ohne Paketkauf im April |

Diese Werte sind durch den fixen Random-Seed reproduzierbar.

## Mit echtem nao laufen lassen

Die `nao_config.yaml` ist heute auf `type: duckdb` gestellt, damit das Demo-Setup
ohne externe Datenbank funktioniert. Für ein nao-Setup mit dem offiziellen
[nao-core CLI](https://docs.getnao.io/nao-agent/quickstart):

```bash
pip install nao-core
# .env mit ANTHROPIC_API_KEY befüllen
nao debug
nao sync
nao chat
nao test         # in einem zweiten Terminal
nao test server  # für die UI auf http://localhost:8765
```

In Produktion wird die DuckDB-Verbindung in `nao_config.yaml` durch eine
PostgreSQL-Verbindung ersetzt – siehe Kommentarblock in der Datei.

## Lizenz

Demo-Code zu Lehrzwecken. Daten sind synthetisch und enthalten keine echten
personenbezogenen Informationen.
