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
- `Colleges` — colleges with their API keys (50 colleges, seeded manually)
- `Enrolments` — per-college student enrolment records, keyed by `(collegeid, idnr, cycle_startdate, cycle_enddate, programme_code)`

**Auth:** API key is looked up in the `Colleges` table via `GET /college` — no hardcoded dict. Every protected endpoint requires `X-API-Key` header. The resolved `collegeid` determines which college the request belongs to.

**Key flow — `/enrolment-check` (POST):**
1. Resolve `collegeid` from API key (Colleges table lookup)
2. Validate `cycle_startdate` and `cycle_enddate` are in `yyyy-mm-dd` format
3. Upsert the `Enrolments` row (insert or update with GMT+2 timestamp)
4. Cross-college duplicate check: query for other colleges that have `enrolled=1` for the same `idnr` with overlapping date range
5. Return `{ status, enrolment, duplicated, duplicates[] }`

**Duplicate records feature:** `/store-duplicates` and `/duplicates-csv` endpoints let the frontend accumulate duplicate records during a bulk import session (keyed by `session_id` query param) and export them as CSV. Storage is in-memory (`duplicate_records_storage` dict) — lost on server restart.

**`import.html`:** Standalone single-page UI that accepts an API key and CSV file, processes rows client-side by calling `/enrolment-check` sequentially, tracks progress, and surfaces duplicates and errors in separate tables after import. The production URL (`studdup.tvet.org.za`) is active; local dev URLs are commented out. CSV format: `cycle_startdate,cycle_enddate,idnr,programme_code,enrolled`.

**`import_csv.py`:** CLI script alternative to the UI — reads `export.csv` (columns: `cycle_startdate,cycle_enddate,idnr,programme_code,enrolled`), calls the production API endpoint, writes results to `results.txt`.

**Performance:** SQLite runs in WAL mode (`journal_mode=WAL`, `synchronous=NORMAL`) for concurrent read/write during bulk imports. Three indexes are created at startup: `(idnr, enrolled)` for the duplicate scan, `(collegeid, idnr, cycle_startdate, cycle_enddate, programme_code)` for upsert lookups, and `(api_key)` on `Colleges` for auth.

## Deployment

Production URL: `https://studdup.tvet.org.za`

The `.venv` directory is committed (Windows venv) — use `.venv\Scripts\activate` on Windows or `.venv/bin/activate` on Linux/Mac.

## Key Constraints

- SQLite file (`studentcheck.db`) is local — not tracked in git (`.gitignore` excludes `*.db`).
- Timestamps use GMT+2 (South African Standard Time) hardcoded as `timedelta(hours=2)`.
- The `docs/` directory is gitignored — it holds sample CSVs and query files used for testing.
