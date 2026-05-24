# studentcheck

## Overview

`main.py` is a FastAPI application for managing student enrolments at South African TVET colleges. It provides endpoints for checking and updating enrolments, listing colleges, and enforces API key authentication for college-specific access.

## Features

- **API Key Authentication:** Each college uses a unique API key resolved against the `Colleges` table. The key determines the `collegeid` for all operations.
- **Enrolment Check:** Add or update a student's enrolment for a date range and programme. Automatically timestamps changes.
- **Duplicate Detection:** Checks if a student is already enrolled at another college for an overlapping date range with `enrolled=1`.
- **Duplicate Export:** Duplicate records collected during a bulk import session can be downloaded as CSV.
- **Error Reporting:** The import UI surfaces per-record errors (invalid dates, HTTP errors, network failures) in a table after import.

## Endpoints

### `POST /enrolment-check`

Upserts a student enrolment and checks for cross-college duplicates.

**Headers:**
- `X-API-Key`: Your college's API key.

**Request Body:**
```json
{
  "idnr": "0401175048563",
  "cycle_startdate": "2025-01-01",
  "cycle_enddate": "2025-12-31",
  "saqa_id": "90772",
  "enrolled": "yes"
}
```

**Response:**
```json
{
  "status": "Added" | "Updated",
  "enrolment": { ... },
  "duplicated": true | false,
  "duplicates": [
    {
      "college_name": "...",
      "idnr": "...",
      "cycle_startdate": "...",
      "cycle_enddate": "...",
      "saqa_id": "...",
      "enrolled": 1
    }
  ]
}
```

On date validation failure:
```json
{ "error": true, "reason": "cycle_startdate must be in yyyy-mm-dd format" }
```

---

### `GET /colleges`

Returns all colleges (id, name, api_key). No auth required.

### `GET /college`

Returns the name and id of the college matching the provided API key.

### `POST /store-duplicates?session_id=<id>`

Stores a list of duplicate records for the given session (in-memory, lost on restart).

### `GET /duplicates-csv?session_id=<id>`

Returns stored duplicate records for the session as a downloadable CSV file.

### `GET /duplicates?session_id=<id>`

Returns stored duplicate records for the session as JSON.

## CSV Format

Required headers (order matters for `import_csv.py`, flexible for `import.html`):

```csv
cycle_startdate,cycle_enddate,idnr,saqa_id,enrolled
2025-01-01,2025-12-31,0401175048563,50203060,yes
```

## Production URL

`https://studdup.tvet.org.za`
