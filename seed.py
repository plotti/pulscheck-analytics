"""
PulsCheck AG – Deterministisches Seed-Skript
=============================================
Erzeugt eine DuckDB-Datenbank mit realistischen Daten:
  - 4'200 Customers
  - ca. 4'500 Subscriptions (inkl. gechurnter)
  - ca. 25'000 Invoices
  - ca. 7'500 Response Packages (S/M/XL)
  - ca. 6'000 Surveys
  - ca. 65'000 Survey Responses
  --> Total > 110'000 Datensätze

Daten reichen vom 2024-01-01 bis 2026-04-30 (Stichtag).
Seed ist fix (random.seed(42)) für reproduzierbare Test-Ergebnisse.
"""

import duckdb
import random
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

# -----------------------------------------------------------
# Konfiguration
# -----------------------------------------------------------
DB_PATH = Path(__file__).parent / "pulscheck.duckdb"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"

random.seed(42)

# Zeit-Setup: Europe/Zurich (UTC+1 Winter, UTC+2 Sommer)
# Vereinfachung: wir nutzen +02:00 für Apr–Okt, +01:00 sonst.
DATA_START = datetime(2024, 1, 1)
DATA_END   = datetime(2026, 4, 30, 23, 59, 59)
NOW        = datetime(2026, 5, 1)  # Stichtag = Anfang Mai 2026

COUNTRIES = ["CH"] * 50 + ["DE"] * 30 + ["AT"] * 10 + ["FR"] * 5 + ["IT"] * 3 + ["GB"] * 2
LANGUAGES_BY_COUNTRY = {
    "CH": ["de", "de", "de", "fr", "fr", "it"],
    "DE": ["de"],
    "AT": ["de"],
    "FR": ["fr", "fr", "en"],
    "IT": ["it", "en"],
    "GB": ["en"],
}

PACKAGE_SPECS = {
    "S":  {"price": 9.0,  "responses": 5_000,   "weight": 50},
    "M":  {"price": 19.0, "responses": 10_000,  "weight": 35},
    "XL": {"price": 29.0, "responses": 100_000, "weight": 15},
}

VAT_RATE = 0.081  # 8.1% Schweizer MwSt

SURVEY_TITLES = [
    "Mitarbeiter-Pulsbefragung Q{q}",
    "Kundenzufriedenheit {y}",
    "Onboarding Feedback",
    "Net Promoter Score {y}",
    "Produktfeedback {month}",
    "Schulungsevaluation",
    "Marktforschung – {topic}",
    "Event-Feedback {event}",
]
SURVEY_TOPICS = ["Nachhaltigkeit", "Digitalisierung", "Home Office", "KI", "Service-Qualität"]
SURVEY_EVENTS = ["Sommerfest", "Q1-Townhall", "Kickoff", "Webinar"]


def iso(dt: datetime) -> str:
    """Liefert ISO-8601 mit Europe/Zurich-Offset (vereinfacht)."""
    month = dt.month
    if 4 <= month <= 9:
        offset = "+02:00"
    else:
        offset = "+01:00"
    return dt.strftime("%Y-%m-%d %H:%M:%S") + offset


def iso_date(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def random_dt_between(start: datetime, end: datetime) -> datetime:
    delta = (end - start).total_seconds()
    return start + timedelta(seconds=random.uniform(0, delta))


def maybe_uuid() -> str:
    return str(uuid.UUID(int=random.getrandbits(128), version=4))


# -----------------------------------------------------------
# Schema laden
# -----------------------------------------------------------
def setup_db() -> duckdb.DuckDBPyConnection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = duckdb.connect(str(DB_PATH))
    conn.execute(SCHEMA_PATH.read_text())
    conn.commit()
    return conn


# -----------------------------------------------------------
# Customers
# -----------------------------------------------------------
def gen_customers(conn: duckdb.DuckDBPyConnection, n: int = 4200):
    rows = []
    for i in range(n):
        cid = maybe_uuid()
        signup = random_dt_between(DATA_START, DATA_END - timedelta(days=1))
        country = random.choice(COUNTRIES)
        # plan-verteilung: ca. 60% aktiv, 8% paused, 17% free, 15% churned
        plan_roll = random.random()
        if plan_roll < 0.60:
            plan = "subscription_active"
        elif plan_roll < 0.68:
            plan = "subscription_paused"
        elif plan_roll < 0.85:
            plan = "free"
        else:
            plan = "churned"
        rows.append((
            cid,
            f"user{i:05d}@example.{country.lower()}",
            iso_date(signup),
            country,
            plan,
            1 if random.random() < 0.6 else 0,
        ))
    conn.executemany(
        "INSERT INTO customers VALUES (?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return rows


# -----------------------------------------------------------
# Subscriptions
# -----------------------------------------------------------
def gen_subscriptions(conn: duckdb.DuckDBPyConnection, customers):
    """
    Regel:
      - subscription_active: started_at vor signup+30, canceled_at NULL
      - subscription_paused: started_at vor signup+30, canceled_at NULL,
                              aber im current_plan paused (vereinfacht: keine separate Pause-Tabelle)
      - churned: started_at gesetzt, canceled_at gesetzt (im Datenraum)
      - free: keine Subscription
    Manche aktive Kund:innen haben in der Vergangenheit auch eine ältere,
    bereits gechurnte Subscription (5%). Das simuliert Re-Activation.
    """
    rows = []
    for cid, _email, signup_date_str, _country, plan, _consent in customers:
        signup = datetime.fromisoformat(signup_date_str)

        if plan == "free":
            continue

        # Mögliche "alte" Sub vor Re-Activation
        if plan == "subscription_active" and random.random() < 0.05:
            old_started = signup + timedelta(days=random.randint(0, 30))
            old_canceled = old_started + timedelta(days=random.randint(60, 240))
            if old_canceled < DATA_END:
                rows.append((
                    maybe_uuid(), cid, iso(old_started), iso(old_canceled), 19.99,
                ))

        # Aktuelle Subscription
        started = signup + timedelta(days=random.randint(0, 14))
        if started > DATA_END:
            continue

        if plan in ("subscription_active", "subscription_paused"):
            canceled = None
        else:  # churned
            min_run = max(1, (DATA_END - started).days // 4)
            canceled = started + timedelta(days=random.randint(min_run, max(min_run + 1, (DATA_END - started).days)))
            if canceled > DATA_END:
                canceled = DATA_END - timedelta(days=random.randint(1, 30))
            if canceled <= started:
                continue

        rows.append((
            maybe_uuid(),
            cid,
            iso(started),
            iso(canceled) if canceled else None,
            19.99,
        ))

    conn.executemany(
        "INSERT INTO subscriptions VALUES (?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return rows


# -----------------------------------------------------------
# Invoices (Subscriptions)
# -----------------------------------------------------------
def gen_subscription_invoices(conn: duckdb.DuckDBPyConnection, subs):
    """
    Eine subscription_invoice pro vollem Monat zwischen started_at
    und (canceled_at oder NOW). Status: 95% paid, 4% failed, 1% refunded.
    """
    rows = []
    for sid, cid, started_iso, canceled_iso, price in subs:
        started = datetime.fromisoformat(started_iso.replace("+02:00", "+02:00").replace("+01:00", "+01:00"))
        # naïv: wir ignorieren timezone für die Schleife
        started = started.replace(tzinfo=None)
        end = (datetime.fromisoformat(canceled_iso.replace("+02:00", "").replace("+01:00", ""))
               if canceled_iso else NOW)

        # erste Rechnung am started_at, dann monatlich
        cur = started
        while cur < min(end, NOW):
            roll = random.random()
            if roll < 0.95:
                status = "paid"
            elif roll < 0.99:
                status = "failed"
            else:
                status = "refunded"
            amount = round(price, 2)
            vat = round(amount - amount / (1 + VAT_RATE), 2)
            rows.append((
                maybe_uuid(), cid, amount, vat, "subscription", status, iso(cur),
            ))
            cur += timedelta(days=30)

    conn.executemany(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return rows


# -----------------------------------------------------------
# Response Packages + zugehörige Invoices
# -----------------------------------------------------------
def gen_response_packages(conn: duckdb.DuckDBPyConnection, customers, subs):
    """
    Nur Subscription-Kund:innen kaufen Pakete (unabhängig von paused/active).
    Verteilung: 50% S, 35% M, 15% XL. Im Schnitt 1.8 Pakete pro Sub-Kunde.
    Jeder Paketkauf erzeugt zusätzlich eine Invoice mit invoice_type='response_package'.
    """
    sub_customer_ids = {row[1] for row in subs}
    pkg_rows = []
    inv_rows = []
    sizes = list(PACKAGE_SPECS.keys())
    weights = [PACKAGE_SPECS[s]["weight"] for s in sizes]

    for cid, _email, signup_date_str, _country, plan, _consent in customers:
        if cid not in sub_customer_ids:
            continue
        signup = datetime.fromisoformat(signup_date_str)
        n_pkgs = random.choices([0, 1, 2, 3, 4, 5, 8], weights=[15, 25, 25, 15, 10, 7, 3])[0]
        for _ in range(n_pkgs):
            size = random.choices(sizes, weights=weights)[0]
            spec = PACKAGE_SPECS[size]
            purchased = random_dt_between(signup, DATA_END)
            used = random.randint(0, spec["responses"])
            pkg_id = maybe_uuid()
            pkg_rows.append((
                pkg_id, cid, size, spec["price"], spec["responses"], used, iso(purchased),
            ))
            # zugehörige Invoice
            roll = random.random()
            status = "paid" if roll < 0.96 else ("failed" if roll < 0.99 else "refunded")
            amount = spec["price"]
            vat = round(amount - amount / (1 + VAT_RATE), 2)
            inv_rows.append((
                maybe_uuid(), cid, amount, vat, "response_package", status, iso(purchased),
            ))

    conn.executemany(
        "INSERT INTO response_packages VALUES (?, ?, ?, ?, ?, ?, ?)",
        pkg_rows,
    )
    conn.executemany(
        "INSERT INTO invoices VALUES (?, ?, ?, ?, ?, ?, ?)",
        inv_rows,
    )
    conn.commit()
    return pkg_rows


# -----------------------------------------------------------
# Surveys
# -----------------------------------------------------------
def gen_surveys(conn: duckdb.DuckDBPyConnection, customers, sub_customer_ids):
    rows = []
    for cid, _email, signup_date_str, country, plan, _consent in customers:
        if cid not in sub_customer_ids:
            continue
        signup = datetime.fromisoformat(signup_date_str)
        n = random.choices([0, 1, 2, 3, 5, 8], weights=[20, 30, 25, 15, 7, 3])[0]
        languages = LANGUAGES_BY_COUNTRY.get(country, ["en"])
        for _ in range(n):
            created = random_dt_between(signup, DATA_END)
            roll = random.random()
            if roll < 0.10:
                status = "draft"
                closed = None
            elif roll < 0.55:
                status = "active"
                closed = None
            else:
                status = "closed"
                closed_dt = created + timedelta(days=random.randint(7, 120))
                closed = iso(closed_dt) if closed_dt < DATA_END else iso(DATA_END)
            tpl = random.choice(SURVEY_TITLES)
            title = tpl.format(
                q=random.randint(1, 4),
                y=random.choice([2024, 2025, 2026]),
                month=created.strftime("%B"),
                topic=random.choice(SURVEY_TOPICS),
                event=random.choice(SURVEY_EVENTS),
            )
            rows.append((
                maybe_uuid(), cid, title, random.choice(languages), status,
                iso(created), closed,
            ))

    conn.executemany(
        "INSERT INTO surveys VALUES (?, ?, ?, ?, ?, ?, ?)",
        rows,
    )
    conn.commit()
    return rows


# -----------------------------------------------------------
# Survey Responses
# -----------------------------------------------------------
def gen_survey_responses(conn: duckdb.DuckDBPyConnection, surveys):
    """
    Pro Survey 0..50 Antworten. Active und closed surveys haben
    deutlich mehr als drafts.
    """
    rows = []
    for sid, cid, _title, language, status, created_iso, closed_iso in surveys:
        created = datetime.fromisoformat(created_iso.replace("+02:00", "").replace("+01:00", ""))
        if status == "draft":
            n = random.choices([0, 1, 2], weights=[80, 15, 5])[0]
        elif status == "active":
            n = random.choices([0, 5, 15, 30, 60, 120], weights=[10, 20, 30, 25, 10, 5])[0]
        else:  # closed
            n = random.choices([0, 10, 25, 50, 100, 200], weights=[5, 15, 30, 30, 15, 5])[0]

        end = datetime.fromisoformat(closed_iso.replace("+02:00", "").replace("+01:00", "")) if closed_iso else min(DATA_END, created + timedelta(days=180))
        for _ in range(n):
            completed = random_dt_between(created, max(end, created + timedelta(hours=1)))
            duration = random.choices(
                [random.randint(45, 120), random.randint(180, 600), random.randint(800, 2400)],
                weights=[20, 65, 15],
            )[0]
            # Respondent-Country: meist gleicher Sprachraum
            if language == "de":
                rc = random.choices(["DE", "CH", "AT"], weights=[55, 30, 15])[0]
            elif language == "fr":
                rc = random.choices(["FR", "CH", "BE"], weights=[60, 30, 10])[0]
            elif language == "it":
                rc = random.choices(["IT", "CH"], weights=[70, 30])[0]
            else:
                rc = random.choices(["GB", "US", "DE", "CH"], weights=[40, 30, 15, 15])[0]
            is_complete = 1 if random.random() < 0.82 else 0
            rows.append((
                maybe_uuid(), sid, iso(completed), duration, rc, is_complete,
            ))

    # Batch-Insert (kann gross werden)
    BATCH = 5000
    for i in range(0, len(rows), BATCH):
        conn.executemany(
            "INSERT INTO survey_responses VALUES (?, ?, ?, ?, ?, ?)",
            rows[i:i + BATCH],
        )
    conn.commit()
    return rows


# -----------------------------------------------------------
# Main
# -----------------------------------------------------------
def main():
    print("Setup DB ...")
    conn = setup_db()

    print("Generating customers ...")
    customers = gen_customers(conn, n=4200)
    print(f"  -> {len(customers):>6} customers")

    print("Generating subscriptions ...")
    subs = gen_subscriptions(conn, customers)
    print(f"  -> {len(subs):>6} subscriptions")

    print("Generating subscription invoices ...")
    sub_invoices = gen_subscription_invoices(conn, subs)
    print(f"  -> {len(sub_invoices):>6} subscription invoices")

    print("Generating response packages + package invoices ...")
    sub_customer_ids = {row[1] for row in subs}
    pkgs = gen_response_packages(conn, customers, subs)
    print(f"  -> {len(pkgs):>6} response packages (incl. invoices)")

    print("Generating surveys ...")
    surveys = gen_surveys(conn, customers, sub_customer_ids)
    print(f"  -> {len(surveys):>6} surveys")

    print("Generating survey responses ...")
    responses = gen_survey_responses(conn, surveys)
    print(f"  -> {len(responses):>6} survey responses")

    # Stats
    cur = conn.cursor()
    print("\nFinal table counts:")
    for table in ["customers", "subscriptions", "invoices",
                  "response_packages", "surveys", "survey_responses"]:
        n = cur.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"  {table:25s} {n:>7}")
    total = cur.execute("""
        SELECT (SELECT COUNT(*) FROM customers)
             + (SELECT COUNT(*) FROM subscriptions)
             + (SELECT COUNT(*) FROM invoices)
             + (SELECT COUNT(*) FROM response_packages)
             + (SELECT COUNT(*) FROM surveys)
             + (SELECT COUNT(*) FROM survey_responses)
    """).fetchone()[0]
    print(f"  {'TOTAL':25s} {total:>7}")

    conn.close()
    print(f"\nDB written to: {DB_PATH}")


if __name__ == "__main__":
    main()
