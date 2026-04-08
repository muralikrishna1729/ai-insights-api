"""
BenefitWhat It Means 
PersistentFiles  survive server restarts
Scalable         Unlimited storage
Decoupled        Any server can access same files
Cheap            Pay only for what you use
"""
import boto3
from app.core.logger import logger 
import os 
import sys
from dotenv import load_dotenv
from botocore.exceptions import ClientError

load_dotenv()


s3_client = boto3.client(
    "s3",
    aws_access_key_id     = os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name           = os.getenv("AWS_REGION")
)

BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

"""
Function receives:
    - file_bytes  → raw bytes of the CSV file
    - filename    → original filename like "sales.csv"
    - job_id      → unique job identifier

Inside:
    - Build s3_key like: "uploads/{job_id}/{filename}"
    - Call s3_client.put_object(...)
    - Return the s3_key

Returns:
    - s3_key (string) → we save this in DB
"""
def upload_file(file_bytes, filename, job_id): 
    try:
        s3_key = f"uploads/{job_id}/{filename}"
        s3_client.put_object(Bucket = BUCKET_NAME, Key = s3_key, Body = file_bytes)
        logger.info(f"file uploaded to {s3_key}")
        return s3_key

    except ClientError as e:
        logger.error(f"S3 upload failed:{e.response['Error']['Code']} -  {str(e)}")
        raise 
        return False


def download_file(s3_key ):
    try:
        response = s3_client.get_object(Bucket=BUCKET_NAME, Key=s3_key)
        file_bytes = response["Body"].read()
        return file_bytes
    except ClientError as e:
        logger.error(f"S3 download failed: {e.response['Error']['Code']} - {str(e)}")
        raise
    