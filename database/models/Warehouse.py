from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship ,backref ,Mapped
import uuid
from typing import Optional , List
from database.base import Base

class WarehouseManager(Base):
    __tablename__ = 'WarehouseManager'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feuser_id = Column(UUID(as_uuid=True), ForeignKey('Field_Exec._id'), nullable=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('Warehouse._id'), nullable=False)
    
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
 
    warehouse : Mapped[Optional["Warehouse"]] = relationship('Warehouse', back_populates='WarehouseManager')
    

class Warehouse(Base):
    __tablename__ = 'Warehouses'
    
    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=True)
    manager = Column(UUID(as_uuid=True), ForeignKey('WarehouseManager._id'), nullable=True)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    warehouse_items : Mapped[List["WarehouseItems"]] = relationship('WarehouseItems', back_populates='warehouse')
    WarehouseManager : Mapped[Optional["WarehouseManager"]] = relationship('WarehouseManager',back_populates = 'warehouse')

class WarehouseItems(Base):
    __tablename__ = 'WarehouseItems'
    
    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('Warehouses._id'), nullable=True)
    product_id = Column(UUID(as_uuid=True), nullable=True)
    quantity = Column(Integer, nullable=True)
    batch_code = Column(UUID(as_uuid=True), nullable=True)
    expiry_date = Column(DateTime, nullable=False, default=func.now())
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationship with Warehouse
    warehouse = relationship('Warehouse', back_populates='warehouse_items')