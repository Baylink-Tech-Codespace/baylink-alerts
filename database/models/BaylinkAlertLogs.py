from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from database.db import Base
import uuid

class BaylinkAlertLogs(Base):
    __tablename__ = 'baylinkalertlogs'

    _id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String(255), nullable=False)
    data = Column(JSON, nullable=True)
    message_type = Column(String(100), nullable=False)
    timestamp = Column(DateTime, default=datetime.now, nullable=False)
    retailer_id = Column(UUID(as_uuid=True), default=uuid.uuid4, nullable=False)

    def __repr__(self):
        return (f"<BaylinkAlertLogs(id={self._id}, retailer_id='{self.retailer_id}', message_type='{self.message_type}', "
                f"timestamp={self.timestamp})>")
