# Todo

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
