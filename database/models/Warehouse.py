from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, JSON
from sqlalchemy.dialects.postgresql import UUID 
from sqlalchemy.orm import relationship ,Mapped
import uuid
from typing import Optional , List
from database.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING: 
    from database.models.Product import Product
    from database.models.Field_Exec import FeUser

class WarehouseManager(Base):
    __tablename__ = 'WarehouseManager'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    feuser_id = Column(UUID(as_uuid=True), ForeignKey('FeUsers._id'), nullable=True)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('Warehouses._id'), nullable=False)
    
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    fe_user : Mapped[Optional["FeUser"]] = relationship('FeUser', back_populates='warehouse_manager')
    warehouse : Mapped[Optional["Warehouse"]] = relationship('Warehouse', back_populates='warehouse_manager')
    

class Warehouse(Base):
    __tablename__ = 'Warehouses'
    
    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    location = Column(String, nullable=True)
    address = Column(JSON, nullable=True)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    warehouse_items : Mapped[List["WarehouseItems"]] = relationship('WarehouseItems', back_populates='warehouse')
    warehouse_manager : Mapped[Optional["WarehouseManager"]] = relationship('WarehouseManager',back_populates = 'warehouse')

class WarehouseItems(Base):
    __tablename__ = 'WarehouseItems'
    
    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    warehouse_id = Column(UUID(as_uuid=True), ForeignKey('Warehouses._id'), nullable=True)
    product_id = Column(UUID(as_uuid=True),ForeignKey('Product._id'), nullable=False)
    quantity = Column(Integer, nullable=True)
    batch_code = Column(UUID(as_uuid=True), nullable=True)
    expiry_date = Column(DateTime, nullable=False, default=func.now())
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationship with Warehouse
    warehouse : Mapped[Optional["Warehouse"]] = relationship('Warehouse', back_populates='warehouse_items')
    product : Mapped[Optional["Product"]] = relationship("Product", back_populates="warehouse_items")