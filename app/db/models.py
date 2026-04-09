"""
Every time someone uploads a CSV → we create a Job

Job has:
- id          (unique identifier)
- filename    (original CSV name)
- s3_key      (where it's stored in S3)
- status      (pending / processing / completed / failed)
- error_msg   (if something went wrong)
- created_at  (when job was created)
"""

from sqlalchemy import Column, String, Integer, Text, DateTime,ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.database import Base

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String, primary_key=True, index = True)
    filename   = Column(String)
    s3_key     = Column(String)
    status     = Column(String, default="pending")
    error_msg  = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    result = relationship("Result", back_populates="job", uselist=False, lazy="select")

class Result(Base):
    __tablename__ = "result"
    id = Column(String, primary_key=True, index = True)
    job_id = Column(String,ForeignKey("jobs.id"),nullable = False)
    quality_score = Column(Integer, default=0)
    quality_detail = Column(Text, nullable=True) 
    anomaly_report = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)    

    job = relationship("Job", back_populates="result", lazy="select")
