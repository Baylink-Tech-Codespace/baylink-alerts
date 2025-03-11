from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Enum, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship, Mapped
from database.base import Base
import uuid
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.Inventory import InventoryStockList
    from database.models.Recon import ReconItem
    from database.models.Sales import Sales
    
class BatchCodes(Base):
    __tablename__ = 'BatchCodes'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    batch_code = Column(String, nullable=True)
    product_id = Column(UUID(as_uuid=True), ForeignKey('Product._id'), nullable=True)
    expiry_date = Column(DateTime, nullable=False, default=func.now())
    createdAt = Column(DateTime, default=func.now(), nullable=False)
    updatedAt = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)

    product: Mapped["Product"] = relationship('Product', back_populates='batch_codes')
    
    def __repr__(self):
        return f"<BatchCodes(batch_code={self.batch_code}, expiry_date={self.expiry_date})>"

class Product(Base):
    __tablename__ = 'Product'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    brand_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
    price_to_retailer = Column(Float, nullable=False)
    MRP = Column(Float, nullable=False)
    MOQ = Column(Float, nullable=True, default=1500)
    image = Column(String, nullable=False)
    LIT_Retailer = Column(Integer, nullable=False, default=2)
    LIT_Baylink = Column(Integer, nullable=False, default=10)
    GST = Column(Float, nullable=False)
    Discount = Column(Float, nullable=True)
    status = Column(Enum('ACTIVE', 'INACTIVE', name='status_enum'), nullable=False, default='ACTIVE')
    category = Column(String, nullable=False, default=' ')
    createdAt = Column(DateTime, server_default=func.now(), nullable=False)
    updatedAt = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    batch_codes: Mapped[List["BatchCodes"]] = relationship('BatchCodes', back_populates='product')
    inventory_stock_list: Mapped[List["InventoryStockList"]] = relationship('InventoryStockList', back_populates='product')
    recon_items : Mapped[List["ReconItem"]] = relationship("ReconItem", back_populates="product")
    sales : Mapped[List["Sales"]] = relationship('Sales', back_populates='product')
    
    @property
    def margin(self):
        if self.MRP and self.price_to_retailer:
            return round(((self.MRP - self.price_to_retailer) / self.MRP) * 100, 0)
        return None
 
   