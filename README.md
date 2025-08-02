# studentcheck

## Overview

`main.py` is a FastAPI application for managing student enrolments at South African TVET colleges. It provides endpoints for checking and updating enrolments, listing cycles and colleges, and enforces API key authentication for college-specific access.

## Features

- **API Key Authentication:** Each college uses a unique API key to access endpoints. The API key determines the `collegeid` for all operations.
- **Enrolment Check:** Add or update a student's enrolment for a cycle and programme. Automatically timestamps changes and checks for duplicate enrolments at other colleges.
- **Cycle and College Listing:** Endpoints to list all cycles and colleges.
- **Duplicate Detection:** When enrolling a student, the API checks if the student is already enrolled at another college for the same cycle and programme.

## Endpoints

### `POST /enrolment-check`

Checks and updates a student's enrolment.  
**Headers:**
- `X-API-Key`: Your college's API key.

**Request Body:**
```json
{
  "idnr": "student_id_number",
  "cycle_name": "2025 - Annual",
  "programme_code": "50203060",
  "enrolled": "YES"
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
      "cycle_name": "...",
      "programme_code": "...",
      "enrolled": 1
    }
  ]
}
```
