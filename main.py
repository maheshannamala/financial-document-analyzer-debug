import os
import uuid
import shutil
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Depends
from sqlalchemy.orm import Session

# Import database configurations and Celery task
# Note: Ensure database.py and celery_worker.py are in the same directory
from database import SessionLocal, engine, Base, AnalysisJob
from celery_worker import process_financial_document

# Create the database tables automatically on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Financial Document Analyzer API (Async)")

# Dependency to get a database session per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "Financial Document Analyzer API is running.",
        "docs": "/docs",
        "endpoints": {
            "POST /analyze": "Upload a PDF to start a background analysis job.",
            "GET /status/{job_id}": "Check the status and get results of a job."
        }
    }

@app.post("/analyze", status_code=202)
async def analyze_financial_document(
    file: UploadFile = File(...),
    query: str = Form(default="Analyze this financial document for investment insights"),
    db: Session = Depends(get_db)
):
    """
    Accepts a file upload, creates a database record, and queues a background task.
    Returns a Job ID immediately so the client doesn't wait.
    """
    # Validate file type
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    job_id = str(uuid.uuid4())
    
    # Create a unique file path
    # Using absolute path ensures the worker (which might run in a different CWD) can find it
    os.makedirs("data", exist_ok=True)
    file_path = os.path.abspath(os.path.join("data", f"{job_id}_{file.filename}"))
    
    try:
        # Save the uploaded file to disk
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create a new job record in the database
        new_job = AnalysisJob(
            id=job_id,
            filename=file.filename,
            query=query,
            status="pending"
        )
        db.add(new_job)
        db.commit()
        db.refresh(new_job)
        
        # Dispatch the task to the Celery worker
        # We pass the file_path so the worker knows what to read
        process_financial_document.delay(job_id=job_id, file_path=file_path, query=query)
        
        return {
            "status": "success",
            "message": "Analysis job submitted successfully.",
            "job_id": job_id,
            "poll_url": f"/status/{job_id}"
        }

    except Exception as e:
        # If submission fails, try to clean up the file
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed to submit job: {str(e)}")

@app.get("/status/{job_id}")
async def get_job_status(job_id: str, db: Session = Depends(get_db)):
    """
    Checks the status of a background job.
    Returns the result if the job is 'completed'.
    """
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job.id,
        "filename": job.filename,
        "status": job.status,
        "submitted_at": job.created_at
    }

    # Include the result only if the job is finished
    if job.status == "completed":
        response["result"] = job.result
    elif job.status == "failed":
        response["error"] = job.result  # In failed state, 'result' column holds the error message

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)