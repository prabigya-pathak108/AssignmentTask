import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Database URL
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USERNAME')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('POSTGRES_DB_PORT')}/{os.getenv('POSTGRES_DATABASE')}"

# Create database engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency for DB session
def get_db():
    """
    Dependency function that provides a SQLAlchemy database session.

    Yields:
        Session: A SQLAlchemy database session.

    Ensures that the session is properly closed after use.
    """

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
