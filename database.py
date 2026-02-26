from sqlalchemy import create_engine, Column, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

# For production, swap this with your PostgreSQL URL: 
# "postgresql://user:password@localhost/dbname"
SQLALCHEMY_DATABASE_URL = "sqlite:///./financial_app.db"

# connect_args is only needed for SQLite
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class AnalysisJob(Base):
    """Database model to store document analysis jobs."""
    __tablename__ = "analysis_jobs"

    id = Column(String, primary_key=True, index=True) # UUID
    filename = Column(String)
    query = Column(String)
    status = Column(String, default="pending") # pending, processing, completed, failed
    result = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)