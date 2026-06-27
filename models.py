from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime
from datetime import datetime
from database import Base

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    stock_symbol = Column(String, index=True)   # e.g. "AAPL"
    target_price = Column(Float)                 # e.g. 150.0
    condition = Column(String)                   # "above" or "below"
    triggered = Column(Boolean, default=False)   # has alert fired yet?
    created_at = Column(DateTime, default=datetime.utcnow)