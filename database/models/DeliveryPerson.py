from sqlalchemy import Column, String, TIMESTAMP, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped
import uuid
from database.base import Base
from sqlalchemy.sql import func
from typing import List , TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.DeliveryLogs import Delivery

class Delivery(Base):
    __tablename__ = 'Delivery'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Name = Column(String, nullable=True)
    Image = Column(ARRAY(String), nullable=True)
    feuser_id = Column(PGUUID(as_uuid=True), nullable=True)
    Contact_Number = Column(String, nullable=True)
    license_no = Column(String, nullable=True)
    vehicle_id = Column(PGUUID(as_uuid=True), nullable=True)

    createdAt = Column(TIMESTAMP, server_default=func.now())
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    
    delivery_logs: Mapped[List["Delivery"]]  = relationship('DeliveryLogs', back_populates='delivery_person')
    
    def __repr__(self):
        return f"<Delivery(name={self.name}, license_no={self.license_no})>"

