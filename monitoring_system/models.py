from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey,Time, Float,JSON
from sqlalchemy.orm import relationship
from .database import Base
from sqlalchemy import Enum, String

StatusEnum = Enum('active', 'inactive', name='status_enum', create_type=False)
statusReport = Enum('Running', 'Complete',"Failed", name='statusReport_enum', create_type=False)
class StoreActivity(Base):
    __tablename__ = "store_activity"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    timestamp_utc = Column(DateTime)
    status = Column(StatusEnum, nullable=False)



class StoreBusinessHours(Base):
    __tablename__ = "store_business_hours"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    day = Column(Integer)
    start_time_local = Column(Time)
    end_time_local = Column(Time)


class StoreTimezone(Base):
    __tablename__ = "store_timezone"

    id = Column(Integer, primary_key=True, index=True)
    store_id = Column(String, index=True)
    timezone_str = Column(String)
class UserReport(Base):
    __tablename__ = "user_reports"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    data=Column(JSON, nullable=True)

    status=Column(statusReport, nullable=True)

