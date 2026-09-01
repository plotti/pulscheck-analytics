-- ============================================================
-- PulsCheck AG – DuckDB Schema
-- ============================================================
-- Survey-SaaS: Subscription (19.99 CHF/Monat) + Pay-per-Use
-- Response Packages S/M/XL (9/19/29 CHF, 5k/10k/100k Antworten)
-- Alle Zeitstempel: ISO 8601 Strings (Europe/Zurich)
-- ============================================================

DROP TABLE IF EXISTS survey_responses;
DROP TABLE IF EXISTS surveys;
DROP TABLE IF EXISTS response_packages;
DROP TABLE IF EXISTS invoices;
DROP TABLE IF EXISTS subscriptions;
DROP TABLE IF EXISTS customers;

-- customers: Stammdaten ----------------------------------------
CREATE TABLE customers (
    id                 TEXT PRIMARY KEY,                     -- UUIDv4
    email              TEXT NOT NULL UNIQUE,
    signup_date        TEXT NOT NULL,                        -- ISO date
    country            TEXT NOT NULL,                        -- ISO-2
    current_plan       TEXT NOT NULL CHECK (current_plan IN
                         ('subscription_active','subscription_paused','free','churned')),
    marketing_consent  INTEGER NOT NULL CHECK (marketing_consent IN (0,1))
);

CREATE INDEX idx_customers_country     ON customers(country);
CREATE INDEX idx_customers_plan        ON customers(current_plan);
CREATE INDEX idx_customers_signup_date ON customers(signup_date);

-- subscriptions: Abo-Historie ----------------------------------
CREATE TABLE subscriptions (
    id                 TEXT PRIMARY KEY,
    customer_id        TEXT NOT NULL REFERENCES customers(id),
    started_at         TEXT NOT NULL,                        -- ISO timestamp
    canceled_at        TEXT,                                 -- NULL = aktiv
    monthly_price_chf  REAL NOT NULL DEFAULT 19.99
);

CREATE INDEX idx_subs_customer_id ON subscriptions(customer_id);
CREATE INDEX idx_subs_started_at  ON subscriptions(started_at);
CREATE INDEX idx_subs_canceled_at ON subscriptions(canceled_at);

-- invoices: Abrechnungen (Subscriptions UND Paketkäufe) --------
CREATE TABLE invoices (
    id            TEXT PRIMARY KEY,
    customer_id   TEXT NOT NULL REFERENCES customers(id),
    amount_chf    REAL NOT NULL,                             -- brutto inkl. MwSt
    vat_chf       REAL NOT NULL,                             -- 8.1% Schweizer MwSt
    invoice_type  TEXT NOT NULL CHECK (invoice_type IN ('subscription','response_package')),
    status        TEXT NOT NULL CHECK (status IN ('paid','failed','refunded')),
    invoiced_at   TEXT NOT NULL
);

CREATE INDEX idx_invoices_customer_id  ON invoices(customer_id);
CREATE INDEX idx_invoices_invoiced_at  ON invoices(invoiced_at);
CREATE INDEX idx_invoices_type         ON invoices(invoice_type);
CREATE INDEX idx_invoices_status       ON invoices(status);

-- response_packages: Pay-per-Use-Paketkäufe --------------------
CREATE TABLE response_packages (
    id                  TEXT PRIMARY KEY,
    customer_id         TEXT NOT NULL REFERENCES customers(id),
    package_size        TEXT NOT NULL CHECK (package_size IN ('S','M','XL')),
    price_chf           REAL NOT NULL,                       -- 9, 19, oder 29
    responses_included  INTEGER NOT NULL,                    -- 5000, 10000, 100000
    responses_used      INTEGER NOT NULL DEFAULT 0,
    purchased_at        TEXT NOT NULL
);

CREATE INDEX idx_pkg_customer_id   ON response_packages(customer_id);
CREATE INDEX idx_pkg_purchased_at  ON response_packages(purchased_at);
CREATE INDEX idx_pkg_size          ON response_packages(package_size);

-- surveys: erstellte Befragungen --------------------------------
CREATE TABLE surveys (
    id           TEXT PRIMARY KEY,
    customer_id  TEXT NOT NULL REFERENCES customers(id),
    title        TEXT NOT NULL,
    language     TEXT NOT NULL CHECK (language IN ('de','fr','it','en')),
    status       TEXT NOT NULL CHECK (status IN ('draft','active','closed')),
    created_at   TEXT NOT NULL,
    closed_at    TEXT
);

CREATE INDEX idx_surveys_customer_id ON surveys(customer_id);
CREATE INDEX idx_surveys_created_at  ON surveys(created_at);
CREATE INDEX idx_surveys_status      ON surveys(status);
CREATE INDEX idx_surveys_language    ON surveys(language);

-- survey_responses: einzelne ausgefüllte Befragungen -----------
CREATE TABLE survey_responses (
    id                         TEXT PRIMARY KEY,
    survey_id                  TEXT NOT NULL REFERENCES surveys(id),
    completed_at               TEXT NOT NULL,
    response_duration_seconds  INTEGER NOT NULL,
    respondent_country         TEXT NOT NULL,
    is_complete                INTEGER NOT NULL CHECK (is_complete IN (0,1))
);

CREATE INDEX idx_resp_survey_id     ON survey_responses(survey_id);
CREATE INDEX idx_resp_completed_at  ON survey_responses(completed_at);
CREATE INDEX idx_resp_is_complete   ON survey_responses(is_complete);
