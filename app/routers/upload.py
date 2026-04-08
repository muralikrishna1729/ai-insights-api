from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.models import Job
from app.db.database import get_db
from app.services.s3_service import upload_file
from app.core.logger import logger
import uuid

router = APIRouter()

def validate_csv(filename:str)->bool:
    return filename.endswith(".csv")

def process_csv(job_id,s3_key,db:Session):
    try:
        job = db.query(Job).filter(Job.id == job_id).first()
        if job:
            job.status = "Processing"
            db.commit()
        
        # TODO code

        job.status = "completed"
        db.commit()
        return job
    except Exception as e:
        logger.error(f"Background job failed: {str(e)}")
        if job:
            job.status = "failed"
            job.error_msg = str(e)
            db.commit()
    finally:
        db.close()


@router.post("/upload")
async def upload(background_tasks: BackgroundTasks,file:UploadFile = File(...),db:Session = Depends(get_db)):
    name = file.filename
    type = file.content_type
    try:
        if validate_csv(name):
            content = await file.read()
            job_id = f"job_{uuid.uuid4().hex[:12]}"
            job = Job(
                id = job_id,
                filename = name,
                s3_key = "",
                status = "pending"
            )
            db.add(job)
            db.commit()

            s3_key = upload_file(content,name,job_id)
            job.s3_key = s3_key
            db.commit()

            background_tasks.add_task(process_csv,job_id,s3_key,db)
            
            return{
                "job_id": job_id,
                "status":"pending",
                "filename":name
            }

        else:
            raise HTTPException(400)
    except HTTPException:
        raise
    except Exception as e:
         logger.error(f"file upload was failed: {str(e)}")
         job.status = "failed"
         job.error_msg = str(e)
         db.commit()
         raise HTTPException(status_code=500, detail="upload failed")


@router.get("/status/{job_id}")
def get_status(job_id:str,db:Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return{
        "job_id":job_id,
        "status":job.status,
        "s3_key": job.s3_key
    }



