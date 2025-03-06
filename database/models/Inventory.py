import uuid
from database.db import Base 
from datetime import datetime
from typing import List,Optional
from database.models.Product import Product
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, JSON
from database.models.Retailer import Retailer 

class Inventory(Base):
    __tablename__ = 'Inventory'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = Column(UUID(as_uuid=True),ForeignKey("Retailer._id"), nullable=True)
    stock_list = Column(JSON, nullable=True, default=[])
    last_updated = Column(DateTime, nullable=False)
    last_updated_by = Column(String, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.now)
    updatedAt = Column(DateTime, nullable=False, default=datetime.now)

    stock_lists: Mapped[List["InventoryStockList"]] = relationship('InventoryStockList', back_populates='inventory')
    retailer: Mapped["Retailer"] = relationship('Retailer', back_populates='inventory')

class InventoryStockList(Base):
    __tablename__ = 'Inventory Stock List'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    inventory_id = Column(UUID(as_uuid=True), ForeignKey('Inventory._id'))
    product_id = Column(UUID(as_uuid=True), ForeignKey('Product._id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.now)
    updatedAt = Column(DateTime, nullable=False, default=datetime.now)

    inventory:  Mapped[Optional["Inventory"]]  = relationship('Inventory', back_populates='stock_lists')
    product: Mapped[Optional["Product"]] = relationship('Product', back_populates='inventory_stock_list')

    @property
    def low_stock(self):
        return self.quantity < 2