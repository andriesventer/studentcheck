# Todo

## Clean up CyclesFact artefacts from DB

**Goal:** The production DB has a leftover `cyclesfact` table and a `cycleid` column in `enrolments`. Remove them at startup; keep `cycle_startdate`/`cycle_enddate` in `enrolments`.

- [x] In `migrate_db()`: drop `cyclesfact` table if it exists
- [x] In `migrate_db()`: drop `cycleid` column from `enrolments` if it exists
- [x] Ensure `cycle_startdate`/`cycle_enddate` ADD COLUMN guards remain (already there, just verify)

## Review

Added two cleanup steps to `migrate_db()` in `main.py`:
- `ALTER TABLE enrolments DROP COLUMN cycleid` — removes the leftover FK column; wrapped in try/except so it's a no-op if the column doesn't exist.
- `DROP TABLE IF EXISTS cyclesfact` — removes the leftover table; safe to re-run.

Both run at every startup before the server accepts requests. No other code was changed.

## SQLite Performance: Indexes + WAL Mode

- [x] Enable WAL mode on the SQLite engine
- [x] Add composite index on `Enrolments(idnr, enrolled)` — speeds up cross-college duplicate scan
- [x] Add composite index on `Enrolments(collegeid, idnr, cycle_startdate, cycle_enddate, programme_code)` — speeds up upsert lookup
- [x] Add index on `Colleges(api_key)` — speeds up auth lookup per request
- [x] Add `create_indexes()` and `enable_wal_mode()` calls at startup

## Review

Added 4 functions to `main.py`, all called at startup:
- `enable_wal_mode()` — sets `journal_mode=WAL` and `synchronous=NORMAL`. WAL allows concurrent reads during writes (bulk imports no longer block reads).
- `create_indexes()` — creates 3 indexes using `IF NOT EXISTS` so they're safe to re-run on every startup.

All indexes are on the existing production DB — they'll be created automatically on next server start with no data migration needed.
