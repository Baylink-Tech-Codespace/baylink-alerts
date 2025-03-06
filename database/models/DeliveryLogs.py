from sqlalchemy import Column, String, Integer, Date, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship,Mapped
from typing import Optional
import uuid
from database.models.DeliveryPerson import Delivery 
from database.base import Base
from database.models.Order import Order

class DeliveryLogs(Base):
    __tablename__ = 'DeliveryLogs'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(PGUUID(as_uuid=True), ForeignKey('Order._id'), nullable=True)
    delivery_person_id = Column(PGUUID(as_uuid=True), ForeignKey('Delivery._id'), nullable=True)
    boxes = Column(Integer, nullable=True)
    date_of_delivery = Column(Date, nullable=True)
    status = Column(String, nullable=True)
    invoice_image = Column(ARRAY(String), nullable=True)
    delivery_image = Column(ARRAY(String), nullable=True)
    notes = Column(String, nullable=True)

    # Relationships
    order: Mapped[Optional["Order"]] = relationship('Order', back_populates='delivery_logs')
    delivery_person: Mapped[Optional["Delivery"]] = relationship('Delivery', back_populates='delivery_logs')

    def __repr__(self):
        return f"<DeliveryLogs(order_id={self.order_id}, status={self.status})>"
 