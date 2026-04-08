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

from sqlalchemy import Column, String, Integer, Text, DateTime
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

