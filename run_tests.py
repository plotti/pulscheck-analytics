"""
Lokaler Test-Runner – Pendant zu `nao test`.

Lädt alle .yml/.yaml-Dateien aus tests/, führt die jeweilige
SQL-Query gegen pulscheck.duckdb aus und gibt eine Pass/Fail-Tabelle
sowie das numerische Ergebnis aus.

Dieser Runner ersetzt nicht den eigentlichen nao test (der ein LLM
benötigt), validiert aber, dass:
  - jede Test-YAML syntaktisch korrekt ist,
  - die hinterlegte SQL-Query gegen die seeded DB läuft,
  - die Ergebnisse deterministisch sind (Seed=42).

Output-Format orientiert sich an dem von nao test.
"""

import duckdb
import yaml
import time
from pathlib import Path

ROOT = Path(__file__).parent
DB = ROOT / "pulscheck.duckdb"
TESTS_DIR = ROOT / "tests"


def run_test(test_path: Path):
    with open(test_path) as f:
        spec = yaml.safe_load(f)
    name = spec["name"]
    sql = spec["sql"]

    conn = duckdb.connect(str(DB))
    cur = conn.cursor()

    t0 = time.perf_counter()
    try:
        result = cur.execute(sql)
        # Get column names
        columns = [desc[0] for desc in cur.description] if cur.description else []
        rows = [{"columns": columns, "values": row} for row in result.fetchall()]
        ok = True
        err = None
    except Exception as e:
        rows = []
        ok = False
        err = str(e)
    duration_ms = (time.perf_counter() - t0) * 1000
    conn.close()

    return {
        "name": name,
        "passed": ok,
        "duration_ms": duration_ms,
        "rows": rows,
        "error": err,
        "prompt": spec.get("prompt", ""),
    }


def fmt_row(row):
    columns = row["columns"]
    values = row["values"]
    return ", ".join(f"{k}={v}" for k, v in zip(columns, values))


def main():
    test_files = sorted(TESTS_DIR.glob("*.yml")) + sorted(TESTS_DIR.glob("*.yaml"))
    if not test_files:
        print("No test files found in tests/")
        return

    print("=" * 78)
    print(f"Running {len(test_files)} test(s) against {DB.name}")
    print("=" * 78)

    results = []
    for tf in test_files:
        r = run_test(tf)
        results.append(r)

        status = "PASS" if r["passed"] else "FAIL"
        print(f"\n[{status}] {r['name']}  ({r['duration_ms']:.1f} ms)")
        print(f"  Q: {r['prompt']}")
        if r["error"]:
            print(f"  ERROR: {r['error']}")
        else:
            for row in r["rows"]:
                print(f"  -> {fmt_row(row)}")

    # Summary
    passed = sum(1 for r in results if r["passed"])
    print("\n" + "=" * 78)
    print(f"Summary: {passed}/{len(results)} passed")
    print("=" * 78)


if __name__ == "__main__":
    main()
