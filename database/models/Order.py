from sqlalchemy import Column, Integer, String, Boolean, Date, Float, UUID, ForeignKey, ARRAY, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped
from typing import Optional 
import uuid
from database.base import Base
from database.models.Retailer import Retailer
from typing import List , TYPE_CHECKING

if TYPE_CHECKING:
    from database.models.DeliveryLogs import DeliveryLogs
    from database.models.Product import Product

class Order(Base):
    __tablename__ = 'Order'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_name = Column(String, nullable=True)
    is_return = Column(Boolean, nullable=False)
    order_date = Column(Date, nullable=False, default=func.now())
    expected_delivery_date = Column(Date, nullable=False, default=func.now())
    order_items = Column(ARRAY(PGUUID(as_uuid=True)), nullable=False, default=[])
    minimum_order_value = Column(Float, nullable=False)
    deal_id = Column(PGUUID(as_uuid=True), nullable=True)
    retailer_id = Column(PGUUID(as_uuid=True), ForeignKey('Retailer._id'), nullable=True)
    status = Column(String, nullable=False)
    isConvertedToInventory = Column(Boolean, nullable=False, default=False)
    billGenerated = Column(Boolean, nullable=False, default=False)
    fe_name = Column(String, nullable=True)
    is_inventory_in = Column(Boolean, nullable=False, default=False)
    feuser_id = Column(PGUUID(as_uuid=True), ForeignKey('FeUser._id'), nullable=True)
    distributor_id = Column(PGUUID(as_uuid=True), nullable=True)

    # Relationships
    #fe_user = relationship('FeUser', back_populates='orders')
    retailer: Mapped[Optional["Retailer"]] = relationship('Retailer', back_populates='orders') 
    delivery_logs: Mapped[List["DeliveryLogs"]]  = relationship('DeliveryLogs', back_populates='order')
    order_items : Mapped[List["OrderItem"]] = relationship("OrderItem", back_populates="order")
    
    #order_items_rel = relationship('OrderItem', back_populates='order')
    

    def __repr__(self):
        return f"<Order(order_name={self.order_name}, status={self.status})>"
    
class OrderItem(Base):
    __tablename__ = 'OrderItem'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(PGUUID(as_uuid=True), ForeignKey('Order._id'), nullable=True)
    product_id = Column(PGUUID(as_uuid=True), ForeignKey('Product._id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    createdAt = Column(Date, nullable=False, default=func.now())
    updatedAt = Column(Date, nullable=False, default=func.now())

    order: Mapped[Optional["Order"]] = relationship("Order", back_populates="order_items")
    product: Mapped[Optional["Product"]] = relationship("Product", back_populates="order_items")


# In FeUser, Retailer, and OrderItem models, you’d add:
# orders = relationship('Order', back_populates='fe_user')
# orders = relationship('Order', back_populates='retailer')
# order = relationship('Order', back_populates='order_items_rel')

# Let me know if you want me to implement the beforeCreate logic for automatic order names! 🚀
