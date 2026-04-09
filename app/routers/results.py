from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Job, Result
from app.core.logger import logger
import json

router = APIRouter()

@router.get("/results/{job_id}")
def get_results(job_id:str, db:Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="job was not found.")

    if job.status != "completed":
        return{
            "job_id" : job_id,
            "status" : job.status,
            "message": "Analysis not ready yet"
        }
    result = db.query(Result).filter(Result.job_id == job_id).first()
    return{
        "job_id"   : job_id,
        "filename" : job.filename,
        "status"   : job.status,
        "quality"  : json.loads(result.quality_detail),
        "anomalies": json.loads(result.anomaly_report)
}


@router.get("/history")
def get_all_jobs(limit:int =10,skip:int=0,db:Session = Depends(get_db)):
    try:
        jobs = db.query(Job).offset(skip).limit(limit).all()
        if not jobs:
            return []
        return jobs
    except Exception as e:
        logger.error(f"Failed to fetch jobs: {str(e)}")
        raise HTTPException(status_code=500, detail="Could not retrieve jobs")