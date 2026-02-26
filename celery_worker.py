import os
from celery import Celery
from crewai import Crew, Process

# Import agents and tasks
from agents import financial_analyst, verifier
from task import analyze_financial_document_task
from database import SessionLocal, AnalysisJob

# Initialize Celery with Redis as the message broker
celery_app = Celery(
    "financial_tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task(bind=True)
def process_financial_document(self, job_id: str, file_path: str, query: str):
    """Background task to run CrewAI analysis and update the database."""
    db = SessionLocal()
    job = db.query(AnalysisJob).filter(AnalysisJob.id == job_id).first()
    
    if not job:
        db.close()
        return

    # Update status to processing
    job.status = "processing"
    db.commit()

    try:
        # Initialize and run the Crew
        financial_crew = Crew(
            agents=[financial_analyst],
            tasks=[analyze_financial_document_task],
            process=Process.sequential,
        )
        
        inputs = {'query': query, 'file_path': file_path}
        result = financial_crew.kickoff(inputs=inputs)
        
        # Save successful results
        job.result = str(result)
        job.status = "completed"
        
    except Exception as e:
        # Log failure
        job.result = f"Error: {str(e)}"
        job.status = "failed"
        
    finally:
        db.commit()
        db.close()
        
        # Clean up the physical file after processing
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass