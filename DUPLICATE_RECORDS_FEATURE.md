# Duplicate Records Detection and Export Feature

## Overview

During a bulk import, the UI detects students already enrolled at another college for an overlapping date range. Duplicates are displayed in a table and can be downloaded as a CSV report. Processing errors (invalid dates, network failures) are shown in a separate table.

## How It Works

### Import Flow

1. User enters API key and selects a CSV file in `import.html`
2. A unique `session_id` is generated client-side (`session_TIMESTAMP_RANDOM`)
3. Each row is posted to `/enrolment-check` sequentially
4. Responses with `duplicated: true` are collected into `allDuplicateRecords`
5. Responses with `error: true` or HTTP errors are collected into `allErrorRecords`
6. After all rows are processed, duplicates are POSTed to `/store-duplicates?session_id=<id>` for server-side CSV export
7. Results page shows: summary stats, duplicates table, errors table

### Duplicate Detection (backend)

The `/enrolment-check` endpoint queries for other colleges where:
- same `idnr`
- `enrolled = 1`
- date ranges overlap: `cycle_startdate <= request.cycle_enddate AND cycle_enddate >= request.cycle_startdate`

### CSV Format

Required headers:
```csv
cycle_startdate,cycle_enddate,idnr,programme_code,enrolled
2025-01-01,2025-12-31,0401175048563,50203060,yes
```

## API Endpoints

### `POST /store-duplicates?session_id=<id>`
Stores duplicate records in memory keyed by session ID. Data is lost on server restart.

### `GET /duplicates-csv?session_id=<id>`
Returns stored duplicates as a downloadable CSV with these columns:
```
Student ID Number, Current College, Conflicting College, Cycle Start Date, Cycle End Date, Programme Code, Enrollment Status, Timestamp
```

### `GET /duplicates?session_id=<id>`
Returns stored duplicates as JSON.

## UI Sections After Import

| Section | Shown when |
|---|---|
| Summary stats | Always (Total, Successful, Duplicates, Errors) |
| Duplicates table | At least one duplicate detected |
| Download button | Duplicates table is visible |
| Errors table | At least one record failed |

## Notes

- Session data is in-memory — lost on server restart. Download the CSV before restarting.
- Multiple colleges can import simultaneously without conflict (each has its own `session_id`).
- The `import.html` file has the production URL (`studdup.tvet.org.za`) active; local dev URLs are commented out.
