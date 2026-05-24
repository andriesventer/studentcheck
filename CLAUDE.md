# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```bash
# Activate virtual environment (Windows)
.venv\Scripts\activate

# Run the API server (development)
uvicorn main:app --reload

# Run the API server (production-style, no reload)
uvicorn main:app --host 0.0.0.0 --port 8000

# Install dependencies
pip install fastapi uvicorn sqlmodel pydantic requests

# Bulk import CSV via script
python import_csv.py
```

The app serves the `import.html` UI at `/` and the API on the same port.

## Architecture

Single-file FastAPI backend (`main.py`) with a SQLite database (`studentcheck.db`), and a standalone HTML/JS frontend (`import.html`) served at the root route.

**Data model:**
- `CyclesFact` — enrolment cycles (e.g. "2025 - Annual", "SEMESTER 1 - FULL TIME - 2025")
- `Colleges` — colleges with their API keys (1–50 colleges hardcoded in `api_keys` dict)
- `Enrolments` — per-college student enrolment records, keyed by `(collegeid, idnr, cycleid, programme_code)`

**Auth:** Hardcoded `api_keys` dict in `main.py` maps API key strings to college IDs (1–50). Every protected endpoint requires `X-API-Key` header. The API key determines which college the request belongs to — there is no other auth layer.

**Key flow — `/enrolment-check` (POST):**
1. Resolve `collegeid` from API key
2. Resolve `cycleid` from `cycle_name`
3. Upsert the `Enrolments` row (insert or update with timestamp)
4. Cross-college duplicate check: query for other colleges that have `enrolled=1` for the same `idnr`
5. Return `{ status, enrolment, duplicated, duplicates[] }`

**Duplicate records feature:** `/store-duplicates` and `/duplicates-csv` endpoints let the frontend accumulate duplicate records during a bulk import session (keyed by `session_id` query param) and export them as CSV. Storage is in-memory (`duplicate_records_storage` dict) — lost on server restart.

**`import.html`:** Standalone single-page UI that accepts an API key and CSV file, processes rows client-side by calling `/enrolment-check` sequentially, tracks progress, and surfaces duplicates. The CSV format is: `cycle,idnr,programme_code,enrolled` (see `docs/sample_test.csv`).

**`import_csv.py`:** CLI script alternative to the UI — reads `export.csv`, calls the production API endpoint, writes results to `results.txt`.

## Deployment

Production URL: `https://studdup.tvet.org.za`

The `.venv` directory is committed (Windows venv) — use `.venv\Scripts\activate` on Windows or `.venv/bin/activate` on Linux/Mac.

## Key Constraints

- API keys are hardcoded in `main.py` — adding a new college requires adding to the `api_keys` dict and inserting a row in `Colleges`.
- SQLite file (`studentcheck.db`) is local — not tracked in git (`.gitignore` excludes `*.db`).
- Timestamps use GMT+2 (South African Standard Time) hardcoded as `timedelta(hours=2)`.
- The `docs/` directory is gitignored — it holds sample CSVs and query files used for testing.
