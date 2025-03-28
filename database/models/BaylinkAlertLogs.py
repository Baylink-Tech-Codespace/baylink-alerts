from sqlalchemy import UUID, Column, Integer, String, DateTime, JSON 
from datetime import datetime
from database.db import Base

import uuid

class BaylinkAlertLogs(Base):
    __tablename__ = 'baylinkalertlogs'

    _id = Column(UUID, primary_key=True,default=uuid.uuid4)
    message = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    person_name = Column(String(255), nullable=False) 
    role = Column(String(255), nullable=False) 
    recepient = Column(String(255), nullable=False)

    def __repr__(self):
        return (f"BaylinkAlertLogs(message={self.message}, timestamp={self.timestamp}, person_name={self.person_name}, role={self.role}, recepient={self.recepient})")
