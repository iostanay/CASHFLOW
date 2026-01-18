from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# MySQL database connection string
# Use environment variable if available (for Railway/deployment), otherwise use default
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:WEQSDeQDqrVjuLifMAysXbrcHwlpcEgV@maglev.proxy.rlwy.net:19323/cashflow_db"
)

# Ensure the DATABASE_URL has the correct format for SQLAlchemy
if DATABASE_URL.startswith("mysql://"):
    DATABASE_URL = DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)

# Create engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_recycle=300,
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """
    Database dependency for FastAPI
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
