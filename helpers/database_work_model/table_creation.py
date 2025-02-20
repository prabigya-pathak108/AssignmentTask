from database import engine
from base import Base  # Your declarative base
from models import Airline, Airport, Flight  # Import models

def init_db():
    """Create tables if they don’t exist"""
    print("🚀 Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

if __name__ == "__main__":  
    init_db()
