from typing import Annotated

from fastapi import Body, Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

class CyclesFact(SQLModel, table=True):
    cycleid: int = Field(default=None, primary_key=True)
    cycle_name: str
    cycle_year: str

class CycleOut(BaseModel):
    cycle_name: str
    cycle_year: str

class EnrolmentCheckIn(BaseModel):
    collegeid: int
    idnr: str
    cycle_name: str
    programme_code: str
    enrolled: str

class Enrolments(SQLModel, table=True):
    rowid: int = Field(default=None, primary_key=True)
    collegeid: int
    idnr: str
    cycleid: int
    programme_code: str
    enrolled: int

class Colleges(SQLModel, table=True):
    collegeid: int = Field(default=None, primary_key=True)
    college_name: str

class CollegeOut(BaseModel):
    collegeid: int
    college_name: str

sqlite_file_name = "studentcheck.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]

app = FastAPI()

@app.get("/cycles", response_model=list[CycleOut])
async def read_cycles(session: SessionDep):
    results = session.exec(select(CyclesFact)).all()
    return results

@app.post("/enrolment-check")
async def enrolment_check(
    session: SessionDep,
    data: EnrolmentCheckIn = Body(...)
):
    # Lookup cycleid from cycle_name
    cycle = session.exec(
        select(CyclesFact).where(CyclesFact.cycle_name == data.cycle_name)
    ).first()
    if not cycle:
        return {"exists": False, "reason": "Cycle not found"}

    # Check if enrolment exists (now includes collegeid)
    enrolment = session.exec(
        select(Enrolments).where(
            (Enrolments.collegeid == data.collegeid) &
            (Enrolments.idnr == data.idnr) &
            (Enrolments.cycleid == cycle.cycleid) &
            (Enrolments.programme_code == data.programme_code)
        )
    ).first()

    enrolled_value = 1 if data.enrolled.lower() == "yes" else 0

    if enrolment:
        # Update enrolled field
        enrolment.enrolled = enrolled_value
        session.add(enrolment)
        session.commit()
        session.refresh(enrolment)
        return {"exists": True, "enrolment": enrolment}
    else:
        # Insert new enrolment
        new_enrolment = Enrolments(
            collegeid=data.collegeid,
            idnr=data.idnr,
            cycleid=cycle.cycleid,
            programme_code=data.programme_code,
            enrolled=enrolled_value
        )
        session.add(new_enrolment)
        session.commit()
        session.refresh(new_enrolment)
        return {"exists": False, "enrolment": new_enrolment}

@app.get("/colleges", response_model=list[CollegeOut])
async def list_colleges(session: SessionDep):
    results = session.exec(select(Colleges)).all()
    return results




