# main.py
import logging

from fastapi import FastAPI, HTTPException, Depends
from databases import Database
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Boolean
from sqlalchemy.sql import select
from pydantic import BaseModel

app = FastAPI()

# Database connection setup
DATABASE_URL = "mysql://root:@localhost/calender"
database = Database(DATABASE_URL)
metadata = MetaData()

# Define the calendars table
calendars = Table(
    "calendars",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String(100)),
    Column("calendar_type", String(100)),
    Column("api_key", String(100)),
    Column("show_busy_only", Boolean, default=False),
    Column("is_private", Boolean, default=False),
)

engine = create_engine(DATABASE_URL)
metadata.create_all(engine)

# Pydantic model for calendar


class CalendarCreate(BaseModel):
    name: str
    calendar_type: str
    api_key: str
    show_busy_only: bool = False
    is_private: bool = False

# Pydantic model for calendar update


class CalendarUpdate(BaseModel):
    name: str
    calendar_type: str
    api_key: str
    show_busy_only: bool
    is_private: bool

# Create a new calendar


@app.post("/calendars/", response_model=CalendarCreate)
async def create_calendar(calendar: CalendarCreate):
    try:
        query = calendars.insert().values(
            name=calendar.name,
            calendar_type=calendar.calendar_type,
            api_key=calendar.api_key,
            show_busy_only=calendar.show_busy_only,
            is_private=calendar.is_private,
        )
        last_record_id = await database.execute(query)
        return {**calendar.dict(), "id": last_record_id}
    except Exception as e:
        logging.exception("An error occurred while creating calendar: %s", e)
        raise

# Read a specific calendar by its ID


@app.get("/calendars/{calendar_id}/", response_model=CalendarCreate)
async def read_calendar(calendar_id: int):
    try:
        query = select([calendars]).where(calendars.c.id == calendar_id)
        calendar = await database.fetch_one(query)
        if calendar is None:
            raise HTTPException(status_code=404, detail="Calendar not found")
        return calendar
    except Exception as e:
        logging.exception("An error occurred while creating calendar: %s", e)
        raise

# Update an existing calendar


@app.put("/calendars/{calendar_id}/", response_model=CalendarCreate)
async def update_calendar(calendar_id: int, calendar: CalendarUpdate):
    query = (
        calendars.update()
        .where(calendars.c.id == calendar_id)
        .values(
            name=calendar.name,
            calendar_type=calendar.calendar_type,
            api_key=calendar.api_key,
            show_busy_only=calendar.show_busy_only,
            is_private=calendar.is_private,
        )
    )
    await database.execute(query)
    return {**calendar.dict(), "id": calendar_id}

# Delete a calendar by its ID


@app.delete("/calendars/{calendar_id}/")
async def delete_calendar(calendar_id: int):
    query = calendars.delete().where(calendars.c.id == calendar_id)
    await database.execute(query)
    return {"message": "Calendar deleted successfully"}


@app.get("/")
async def read_root():
    return {"message": "Hello, FastAPI!"}

# Configure logging to write to a file
logging.basicConfig(
    filename='app.log',  # Specify the log file name
    level=logging.DEBUG,  # Set the logging level
    # Set the log message format
    format='%(asctime)s - %(levelname)s - %(message)s'
)


@app.on_event("startup")
async def startup():
    try:
        await database.connect()
    except Exception as e:
        logging.error("Failed to connect to the database: %s", e)


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
