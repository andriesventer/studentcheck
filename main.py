from typing import Annotated
from datetime import datetime, timedelta, timezone

from fastapi import Body, Depends, FastAPI, Header, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select
from pydantic import BaseModel

api_keys={
"6RDGH9fMHHTvCiQbmBKRnat77Y49vS0p":"1",
"WQzClfZ8GbXyY4v7O13LB3g2q0iVvcdb":"2",
"ub9q4TjteXiFPl5Y4olcQELjub9pVwSd":"3",
"5HuI73vhFtHCo52neaMFJCm9qQFcvPv4":"4",
"UjWmcttALKvqi27Vfv5mymGS05r9qV6j":"5",
"Een6ySLt20yQQMTDcSvYN0t1hQnyaa5o":"6",
"XPJzJvSltXeoPGiyYvwGvopqqTUfk6RO":"7",
"Jggxu9XsJSVfTt8vnoqCS9DwT0eTN2Jj":"8",
"wiLUUsws5XyD9Hsv7QEjRxp2W5GTK04b":"9",
"dkWl7a1GWyLlHMklpO5hl9ZO3Q9ugUbw":"10",
"L64SWfRZbGuO0jPegxHGp01FIrXDhAlh":"11",
"bjQSzk6Jby127CmmEvsDjtaXndzuXaKk":"12",
"2444EfAlQo7FwNqvz2j9ziGZK99GbXxc":"13",
"MrpNsijS74kDWsNT2ObrV9hRtB8t73TC":"14",
"oIDvIH9ouFsMbN62I44IKx7vxpO9cWDU":"15",
"1fpW8oXhLm0992KLPnWikS24PFIOQq3o":"16",
"4arvvshaVJobKxjm3WZAtV4Jru8yd8wQ":"17",
"pEXCgyVulFSspJGvs3ulrJwIECEjC1CQ":"18",
"fUAxdO3OKE3lMymqN3nwrp0mOY9x6BzD":"19",
"gwkor6W9Blqhhj0Ry6sMWtp2sgp8rZ4c":"20",
"w8E41nhLxQpBdUva1xENDa2qTgvDgeWW":"21",
"WKL5jrz19JomNiXWD30wlieOMnk51Mq6":"22",
"0YybeOGYZlCNrwyeHNKYiMrj0miqOVnL":"23",
"LWJvIgSOtSWoOixl5zA5Z9RocXSh5LJh":"24",
"NvOVJFMwRebZRnryXpVGWU5z4zW3hoS8":"25",
"LzGETdhAvIX7Cfg1q0tPDhNPsm2F2b2h":"26",
"0Nk0G9LxrPcdxu00uYpgGXNDPpoBlGdl":"27",
"HxEBXm8dcoQUgr0wXrUIZBNM9mgxZKmU":"28",
"KVhm2gXzXtEruU21zTO8wc45klxNxBT8":"29",
"XO7u7fC36b9O1uldLbRj2oPnDwt4s2Bv":"30",
"h5lSYnYaLv2KPNAJrFEtN9SG0sn8Hehj":"31",
"kEJAUGy2Q2n3jqqb5p2QmPpiqfHCGWzT":"32",
"pH0loubW0CFkcv6H8WjudCbrK4q0B1TK":"33",
"X4iVe9qv5CTpO5wGlzvLF0fFmw4ySxl7":"34",
"CujJViInuqXlIKAixUKFffTu3U5AZ4aa":"35",
"Zjd4bItkGVVyTgsxlmZgRz2uVxLWyIi8":"36",
"Fxw67eXwdbCGa33fxQ2RO33LMMs0V78V":"37",
"EXhJxJKiLglTNEemCUq20ckSS9xmVBq4":"38",
"OZEuZLZvg1XzjcuqgzXIAQmBjVZPDEqX":"39",
"NiIbivUQp40ZGnItqmbxBIDwO0Fw9aCI":"40",
"9RvI4bhuAJC6M46g0il87t2QWWEut4nV":"41",
"thHfS77V8I2QOwzfdWO8mrM0tKaf0wFL":"42",
"Wk2Ef1bKKWU2R3e20m6vwf56Ei2Yn7kR":"43",
"X94nYQPAPuBQ3Wq75gABZfPHYxOq0WnR":"44",
"YRSRs6I6NADfc3fO4qQ6BwGkK5DyhcUt":"45",
"mglSViwS6KC45Qi1LIW8VBisQC4XzbUr":"46",
"PwvRDJ3CrbhfwPYiH6RxUwOjlAnVS3rw":"47",
"FFkJ2CbTkxy3Wkm3e57fSvS8fnHIl6tz":"48",
"774sadWNyoJrgO9JWAJ4HnsoKiBNkJoR":"49",
"Yo2CFWRPJLJoGKWCQZ8NaQLgFSceHIXO":"50"
}

class CyclesFact(SQLModel, table=True):
    cycleid: int = Field(default=None, primary_key=True)
    cycle_name: str
    cycle_year: str

class CycleOut(BaseModel):
    cycle_name: str
    cycle_year: str

class EnrolmentCheckIn(BaseModel):
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
    timestamp: str  # New field for timestamp

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

app = FastAPI(docs_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify ["http://localhost:5500"] for Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/cycles", response_model=list[CycleOut])
async def read_cycles(session: SessionDep):
    results = session.exec(select(CyclesFact)).all()
    return results

def get_api_key(
    x_api_key: str = Header(..., alias="X-API-Key")
):
    if x_api_key not in api_keys:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
    return x_api_key

@app.post("/enrolment-check")
async def enrolment_check(
    session: SessionDep,
    data: EnrolmentCheckIn = Body(...),
    api_key: str = Depends(get_api_key)
):
    # Get collegeid from api_keys using the provided API key
    collegeid = int(api_keys[api_key])

    # Lookup cycleid from cycle_name
    cycle = session.exec(
        select(CyclesFact).where(CyclesFact.cycle_name == data.cycle_name)
    ).first()
    if not cycle:
        return {
            "error": True,
            "reason": "Cycle not found"
        }

    # Check if enrolment exists (now includes collegeid)
    enrolment = session.exec(
        select(Enrolments).where(
            (Enrolments.collegeid == collegeid) &
            (Enrolments.idnr == data.idnr) &
            (Enrolments.cycleid == cycle.cycleid) &
            (Enrolments.programme_code == data.programme_code)
        )
    ).first()

    enrolled_value = 1 if data.enrolled.lower() == "yes" else 0
    gmt_plus_2 = timezone(timedelta(hours=2))
    now = datetime.now(gmt_plus_2).isoformat()

    # Check for duplicate enrolment at another college
    duplicate_query = (
        select(
            Colleges.college_name,
            Enrolments.idnr,
            CyclesFact.cycle_name,
            Enrolments.programme_code,
            Enrolments.enrolled
        )
        .join(CyclesFact, Enrolments.cycleid == CyclesFact.cycleid)
        .join(Colleges, Colleges.collegeid == Enrolments.collegeid)
        .where(
            (Enrolments.idnr == data.idnr) &
            (Enrolments.collegeid != collegeid) &
            (Enrolments.enrolled == 1)
        )
    )
    duplicates = session.exec(duplicate_query).all()
    duplicated = len(duplicates) > 0

    if enrolment:
        # Update enrolled field and timestamp
        enrolment.enrolled = enrolled_value
        enrolment.timestamp = now
        session.add(enrolment)
        session.commit()
        session.refresh(enrolment)
        enrolment_dict = enrolment.dict()
        enrolment_dict["cycle_name"] = cycle.cycle_name
        enrolment_dict.pop("cycleid", None)
        return {
            "status": "Updated",
            "enrolment": enrolment_dict,
            "duplicated": duplicated,
            "duplicates": [dict(zip(["college_name", "idnr", "cycle_name", "programme_code", "enrolled"], d)) for d in duplicates]
        }
    else:
        # Insert new enrolment with timestamp
        new_enrolment = Enrolments(
            collegeid=collegeid,
            idnr=data.idnr,
            cycleid=cycle.cycleid,
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
            "duplicates": [dict(zip(["college_name", "idnr", "cycle_name", "programme_code", "enrolled"], d)) for d in duplicates]
        }

@app.get("/colleges", response_model=list[CollegeOut])
async def list_colleges(session: SessionDep):
    results = session.exec(select(Colleges)).all()
    return results




