from sqlalchemy import Column, DateTime, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from database.models.Retailer import Retailer
from database.models.Product import BatchCodes
from database.models.Product import Product
from typing import Optional
from database.base import Base
import uuid

class Sales(Base):
    __tablename__ = 'sales'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = Column(UUID(as_uuid=True), ForeignKey('Retailer._id'), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey('Product._id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    date = Column(DateTime, nullable=False)
    
    # Relationships
    product: Mapped[Optional["Product"]] = relationship('Product', back_populates='sales')
    retailer: Mapped[Optional["Retailer"]] = relationship('Retailer', back_populates='sales')
    #batch_codes: Mapped[Optional["BatchCodes"]] = relationship('BatchCodes', back_populates='sales')

    def __repr__(self):
        return f"<Sales(id={self._id}, retailer_id={self.retailer_id}, product_id={self.product_id}, quantity={self.quantity}, date={self.date})>"
    
    def __str__(self):
        return f"<Sales(id={self._id}, retailer_id={self.retailer_id}, product_id={self.product_id}, quantity={self.quantity}, date={self.date})>"
    
    
    