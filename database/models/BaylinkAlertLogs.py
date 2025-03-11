from sqlalchemy import Column, Integer, String, DateTime, JSON 
from datetime import datetime
from database.db import Base

class BaylinkAlertLogs(Base):
    __tablename__ = 'baylinkalertlogs'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    person_name = Column(String(255), nullable=False) 
    role = Column(String(255), nullable=False) 

    def __repr__(self):
        return (f"<BaylinkAlertLogs(id={self._id}, retailer_id='{self.retailer_id}', "
                f"timestamp={self.timestamp})>")
