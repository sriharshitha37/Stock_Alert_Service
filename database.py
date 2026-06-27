from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# This creates a local SQLite file called stock_alerts.db
SQLALCHEMY_DATABASE_URL = "sqlite:///./stock_alerts.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This function gives us a DB session for each API request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()