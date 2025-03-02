from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Database connection configuration
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql://kartikvadhawana:kartik123@localhost/football_prediction_db"
)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for declarative models
Base = declarative_base()

def get_db():
    """
    Dependency that creates a new database session for each request
    and closes it after the request is completed
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Function to create all tables
def create_tables():
    Base.metadata.create_all(bind=engine)

# Optional: Function to drop all tables (use with caution)
def drop_tables():
    Base.metadata.drop_all(bind=engine)