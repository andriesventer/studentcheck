from typing import Annotated
from datetime import datetime, timedelta, timezone
import csv
import io

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select, text
from pydantic import BaseModel


class EnrolmentCheckIn(BaseModel):
    idnr: str
    cycle_startdate: str
    cycle_enddate: str
    programme_code: str
    enrolled: str

class Enrolments(SQLModel, table=True):
    rowid: int = Field(default=None, primary_key=True)
    collegeid: int
    idnr: str
    cycle_startdate: str
    cycle_enddate: str
    programme_code: str
    enrolled: int
    timestamp: str

class Colleges(SQLModel, table=True):
    collegeid: int = Field(default=None, primary_key=True)
    college_name: str
    api_key: str

class CollegeOut(BaseModel):
    collegeid: int
    college_name: str

class DuplicateRecord(BaseModel):
    student_idnr: str
    current_college: str
    conflicting_college: str
    cycle_startdate: str
    cycle_enddate: str
    programme_code: str
    enrolled_status: str
    timestamp: str

# In-memory storage for duplicate records during import sessions
duplicate_records_storage = {}

sqlite_file_name = "studentcheck.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def enable_wal_mode():
    with engine.connect() as conn:
        conn.execute(text("PRAGMA journal_mode=WAL"))
        conn.execute(text("PRAGMA synchronous=NORMAL"))


def create_indexes():
    with engine.connect() as conn:
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_enrolments_idnr_enrolled "
            "ON enrolments (idnr, enrolled)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_enrolments_upsert "
            "ON enrolments (collegeid, idnr, cycle_startdate, cycle_enddate, programme_code)"
        ))
        conn.execute(text(
            "CREATE INDEX IF NOT EXISTS idx_colleges_api_key "
            "ON colleges (api_key)"
        ))
        conn.commit()


def migrate_db():
    with engine.connect() as conn:
        # Ensure date columns exist (legacy guard)
        for col in ("cycle_startdate", "cycle_enddate"):
            try:
                conn.execute(text(f"ALTER TABLE enrolments ADD COLUMN {col} TEXT"))
                conn.commit()
            except Exception:
                pass
        # Remove leftover cycleid column from enrolments if present
        try:
            conn.execute(text("ALTER TABLE enrolments DROP COLUMN cycleid"))
            conn.commit()
        except Exception:
            pass
        # Drop leftover cyclesfact table if present
        try:
            conn.execute(text("DROP TABLE IF EXISTS cyclesfact"))
            conn.commit()
        except Exception:
            pass


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI(docs_url=None)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    migrate_db()
    enable_wal_mode()
    create_indexes()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5500"] for Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the import.html file at the root URL"""
    with open("import.html", "r", encoding="utf-8") as file:
        html_content = file.read()
    return HTMLResponse(content=html_content)

def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key"),
    session: Session = Depends(get_session)
) -> int:
    college = session.exec(
        select(Colleges).where(Colleges.api_key == x_api_key)
    ).first()
    if not college:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return college.collegeid

@app.post("/enrolment-check")
async def enrolment_check(
    session: SessionDep,
    data: EnrolmentCheckIn = Body(...),
    collegeid: int = Depends(get_api_key)
):
    # Validate date formats
    for field_name, value in [("cycle_startdate", data.cycle_startdate), ("cycle_enddate", data.cycle_enddate)]:
        try:
            datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return {"error": True, "reason": f"{field_name} must be in yyyy-mm-dd format"}

    enrolled_value = 1 if data.enrolled.lower() == "yes" else 0
    gmt_plus_2 = timezone(timedelta(hours=2))
    now = datetime.now(gmt_plus_2).isoformat()

    # Check if enrolment exists for this college/student/period/programme
    enrolment = session.exec(
        select(Enrolments).where(
            (Enrolments.collegeid == collegeid) &
            (Enrolments.idnr == data.idnr) &
            (Enrolments.cycle_startdate == data.cycle_startdate) &
            (Enrolments.cycle_enddate == data.cycle_enddate) &
            (Enrolments.programme_code == data.programme_code)
        )
    ).first()

    # Duplicate: same student, different college, enrolled=1, overlapping date range
    duplicate_query = (
        select(
            Colleges.college_name,
            Enrolments.idnr,
            Enrolments.cycle_startdate,
            Enrolments.cycle_enddate,
            Enrolments.programme_code,
            Enrolments.enrolled
        )
        .join(Colleges, Colleges.collegeid == Enrolments.collegeid)
        .where(
            (Enrolments.idnr == data.idnr) &
            (Enrolments.collegeid != collegeid) &
            (Enrolments.enrolled == 1) &
            (Enrolments.cycle_startdate <= data.cycle_enddate) &
            (Enrolments.cycle_enddate >= data.cycle_startdate)
        )
    )
    duplicates = session.exec(duplicate_query).all()
    duplicated = len(duplicates) > 0

    if enrolment:
        enrolment.enrolled = enrolled_value
        enrolment.timestamp = now
        session.add(enrolment)
        session.commit()
        session.refresh(enrolment)
        return {
            "status": "Updated",
            "enrolment": enrolment.dict(),
            "duplicated": duplicated,
            "duplicates": [dict(zip(["college_name", "idnr", "cycle_startdate", "cycle_enddate", "programme_code", "enrolled"], d)) for d in duplicates]
        }
    else:
        new_enrolment = Enrolments(
            collegeid=collegeid,
            idnr=data.idnr,
            cycle_startdate=data.cycle_startdate,
            cycle_enddate=data.cycle_enddate,
            programme_code=data.programme_code,
            enrolled=enrolled_value,
            timestamp=now
        )
        session.add(new_enrolment)
        session.commit()
        session.refresh(new_enrolment)
        return {
            "status": "Added",
            "enrolment": new_enrolment,
            "duplicated": duplicated,
            "duplicates": [dict(zip(["college_name", "idnr", "cycle_startdate", "cycle_enddate", "programme_code", "enrolled"], d)) for d in duplicates]
        }

@app.get("/colleges", response_model=list[CollegeOut])
async def list_colleges(session: SessionDep):
    results = session.exec(select(Colleges)).all()
    return results

@app.get("/college")
async def get_current_college(
    session: SessionDep,
    collegeid: int = Depends(get_api_key)
):
    """Get college information for the authenticated user"""
    college = session.exec(
        select(Colleges).where(Colleges.collegeid == collegeid)
    ).first()
    
    if not college:
        raise HTTPException(status_code=404, detail="College not found")
    
    return {
        "collegeid": college.collegeid,
        "college_name": college.college_name
        # Note: We don't return the API key for security
    }

@app.post("/store-duplicates")
async def store_duplicates(
    session_id: str = Query(...),
    duplicates: list[DuplicateRecord] = Body(...),
    _: int = Depends(get_api_key)
):
    """Store duplicate records for a session"""
    duplicate_records_storage[session_id] = duplicates
    return {"status": "success", "stored_count": len(duplicates)}

@app.get("/duplicates-csv")
async def export_duplicates_csv(
    session_id: str = Query(...),
    _: int = Depends(get_api_key)
):
    """Export duplicate records as CSV"""
    if session_id not in duplicate_records_storage:
        raise HTTPException(status_code=404, detail="No duplicate records found for this session")
    
    duplicates = duplicate_records_storage[session_id]
    
    # Create CSV content
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header
    writer.writerow([
        "Student ID Number",
        "Current College",
        "Conflicting College",
        "Cycle Start Date",
        "Cycle End Date",
        "Programme Code",
        "Enrollment Status",
        "Timestamp"
    ])

    # Write data rows
    for duplicate in duplicates:
        writer.writerow([
            duplicate.student_idnr,
            duplicate.current_college,
            duplicate.conflicting_college,
            duplicate.cycle_startdate,
            duplicate.cycle_enddate,
            duplicate.programme_code,
            duplicate.enrolled_status,
            duplicate.timestamp
        ])
    
    output.seek(0)
    
    # Generate filename with timestamp
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"duplicate_records_{now}.csv"
    
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@app.get("/duplicates")
async def get_duplicates(
    session_id: str = Query(...),
    _: int = Depends(get_api_key)
):
    """Get duplicate records for a session"""
    if session_id not in duplicate_records_storage:
        return {"duplicates": []}
    
    return {"duplicates": duplicate_records_storage[session_id]}
