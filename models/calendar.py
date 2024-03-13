# models/calendar.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Calendar(Base):
    __tablename__ = 'calendars'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    calendar_type = Column(String)
    api_key = Column(String)
    show_busy_only = Column(Boolean, default=False)
    is_private = Column(Boolean, default=False)
    
    
    
class Times(Base):
    __tablename__ = 'times'
    
    id = Column(Integer, primary_key=True, index=True)
    time_date = Column(DateTime)

