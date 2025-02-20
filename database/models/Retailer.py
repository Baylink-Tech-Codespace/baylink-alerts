from sqlalchemy import Column, String, ForeignKey, JSON, DECIMAL, Enum, DateTime, UUID
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy.ext.declarative import declarative_base
import uuid
from typing import List, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from database.models.Recon import Recon

Base = declarative_base()

class Retailer(Base):
    __tablename__ = "Retailer"

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    area_id = Column(UUID(as_uuid=True), ForeignKey("Area._id"), nullable=True)
    name = Column(String, nullable=False)
    POC_name = Column(String, nullable=False)
    phone_no = Column(String, nullable=False)
    address = Column(JSON, nullable=False)
    GSTIN = Column(String, nullable=True)
    FE_id = Column(UUID(as_uuid=True), ForeignKey("Field_Exec._id"), nullable=True)
    ASM_id = Column(UUID(as_uuid=True), ForeignKey("ASM._id"), nullable=True)
    closing_balance = Column(DECIMAL(10, 2), nullable=True)
    image = Column(String, nullable=True)
    outsideImage = Column(String, nullable=True)
    storeCategory = Column(Enum("null", "undefined", "Grocery", "Convenience store", "Bakery", "Pharmacy", "Paan Shop", "Other"), nullable=True)
    storeFootfall = Column(String, nullable=True)
    popularCategories = Column(Enum("null", "undefined", "Fruits and vegetables", "Daily Ration", "Dairy", "Frozen Food", "Beverages", "Home Goods"), nullable=True)
    popularCategoriesMultiple = Column(JSON, nullable=True)
    inventoryTurnover = Column(Enum("null", "undefined", "3 Days", "5 Days", "7 Days", ">7 Days"), nullable=True)
    dailyTurnover = Column(String, nullable=True)
    shopAOV = Column(String, nullable=True)
    storeSize = Column(String, nullable=True)
    FERating = Column(String, nullable=True)
    operatingHours = Column(JSON, nullable=True)
    storeStatus = Column(Enum("null", "undefined", "Onboarded", "Followup", "Not Onboarded", "Inactive", "Prospect"), nullable=True)
    followUpDate = Column(DateTime, nullable=True)
    reason = Column(String, nullable=True)
    feedback = Column(String, nullable=True)
    brandsPitched = Column(JSON, nullable=True)
    googleRating = Column(String, nullable=True)
    paymentRating = Column(String, nullable=True)
    prefDeliveryTime = Column(JSON, nullable=True)
    collectionDay = Column(Enum("null", "undefined", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"), nullable=True)
    collectionTime = Column(JSON, nullable=True)
    lastVisited = Column(DateTime, nullable=True)
    nextVisit = Column(DateTime, nullable=True)
    fssaiCode = Column(String, nullable=True)
    fssaiImage = Column(String, nullable=True)
    createdAt = Column(DateTime, default=datetime.utcnow, nullable=False)
    updatedAt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.now, nullable=False)
 
    #Recon: Mapped[List["Recon"]] = relationship("Recon", back_populates="Retailer")
