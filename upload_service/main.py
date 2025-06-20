from fastapi import FastAPI, UploadFile, File, HTTPException
from s3 import upload_to_s3, s3_object_exists
from k8s import create_processor_job
import uuid, os

app = FastAPI()
S3_BUCKET = os.environ["S3_BUCKET"]

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    job_id = str(uuid.uuid4())
    key = f"uploads/{job_id}.zip"
    contents = await file.read()

    try:
        upload_to_s3(contents, key, S3_BUCKET)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"S3 upload failed: {str(e)}")

    if not s3_object_exists(S3_BUCKET, key):
        raise HTTPException(status_code=500, detail="S3 upload verification failed")

    try:
        create_processor_job(job_id, key)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"K8s job creation failed: {str(e)}")

    return {"job_id": job_id, "s3_key": key, "status": "job_created"}
