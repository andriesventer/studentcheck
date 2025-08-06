# Duplicate Records Detection and Export Feature

## Overview

This feature enhancement adds comprehensive duplicate record detection and reporting capabilities to the Student Enrolment Import system. When duplicate student enrolments are detected during the import process, they are collected, displayed in a table, and made available for download as a CSV report.

## Features Added

### 1. Backend API Enhancements (main.py)

#### New Endpoints:
- **POST /store-duplicates**: Stores duplicate records for a session
- **GET /duplicates-csv**: Exports duplicate records as a downloadable CSV file
- **GET /duplicates**: Retrieves duplicate records for a session

#### New Data Models:
- **DuplicateRecord**: Pydantic model for structured duplicate record data
- **duplicate_records_storage**: In-memory storage for session-based duplicate tracking

### 2. Frontend Enhancements (import.html)

#### New UI Components:
- **Duplicates Table**: Displays all detected duplicate records in a formatted table
- **Download Button**: Allows users to download duplicate records as CSV
- **Enhanced Progress Tracking**: Real-time collection of duplicate data during import

#### New JavaScript Functions:
- **generateSessionId()**: Creates unique session identifiers
- **getCollegeName()**: Fetches actual college names from API
- **downloadDuplicatesCSV()**: Handles CSV file download

## How It Works

### 1. Import Process Flow
1. User uploads CSV file and enters API key
2. System generates unique session ID
3. Each record is processed through the `/enrolment-check` endpoint
4. Duplicate records are collected in real-time
5. All duplicates are stored on the server with session ID
6. Results are displayed with summary statistics and duplicate table

### 2. Duplicate Detection Logic
- During enrolment check, the system queries for existing enrolments
- If a student is already enrolled at another college for the same cycle/programme
- The duplicate information is captured including:
  - Student ID Number
  - Current College (attempting to enroll)
  - Conflicting College (where already enrolled)
  - Cycle Name
  - Programme Code
  - Enrollment Status
  - Timestamp

### 3. Data Export
- Duplicates are stored server-side with session-based keys
- CSV export includes all duplicate records with proper headers
- File naming includes timestamp for easy identification
- Download is triggered via browser download mechanism

## Usage Instructions

### For End Users:
1. Open the import interface (`import.html`)
2. Enter your college API key
3. Select CSV file with student data
4. Click "Import" to start processing
5. Monitor progress bar during import
6. Review summary statistics upon completion
7. If duplicates are found:
   - View detailed table of all duplicate records
   - Click "Download Duplicates Report (CSV)" to export data

### CSV File Format:
Required headers: `cycle`, `idnr`, `programme_code`, `enrolled`

Example:
```csv
cycle,idnr,programme_code,enrolled
2025 - Annual,0401175048563,50203060,yes
2025 - Annual,9876543210123,50203061,yes
```

## Technical Implementation Details

### Session Management
- Each import session gets a unique ID: `session_TIMESTAMP_RANDOMSTRING`
- Duplicate records are stored in memory with session key
- Session data persists until server restart (suitable for short-term reporting)

### API Integration
- All existing endpoints remain unchanged
- New endpoints follow existing authentication patterns
- CORS enabled for frontend integration
- Error handling for missing sessions or invalid requests

### Frontend Architecture
- Async/await pattern for API calls
- Real-time progress updates
- Responsive design for mobile compatibility
- Error handling with user-friendly messages

## File Structure

```
studentcheck/
├── main.py                          # Enhanced FastAPI backend
├── import.html                      # Enhanced frontend interface
├── sample_test.csv                  # Sample CSV for testing
├── DUPLICATE_RECORDS_FEATURE.md     # This documentation
└── README.md                        # Original project documentation
```

## Example Duplicate Record Output

### Table Display:
| Student ID | Current College | Conflicting College | Cycle | Programme Code | Status |
|------------|----------------|-------------------|-------|----------------|--------|
| 0401175048563 | Boland TVET College | Western Cape College | 2025 - Annual | 50203060 | Yes |

### CSV Export Format:
```csv
Student ID Number,Current College,Conflicting College,Cycle Name,Programme Code,Enrollment Status,Timestamp
0401175048563,Boland TVET College,Western Cape College,2025 - Annual,50203060,Yes,2025-08-05T17:48:27.796Z
```

## Benefits

1. **Immediate Visibility**: Users can see duplicate records as soon as import completes
2. **Detailed Information**: Full context about conflicting enrolments
3. **Export Capability**: CSV download for further analysis or reporting
4. **User-Friendly Interface**: Clean, responsive design with clear visual indicators
5. **Session-Based**: Multiple users can import simultaneously without conflicts
6. **Real-Time Processing**: Duplicates detected and collected during import process

## Future Enhancements

Potential improvements could include:
- Persistent storage for duplicate records
- Email notifications for duplicate alerts
- Bulk resolution workflows
- Historical duplicate tracking
- Advanced filtering and search capabilities
