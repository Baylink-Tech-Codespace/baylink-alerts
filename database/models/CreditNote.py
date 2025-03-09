from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, UUID, ARRAY, func
from sqlalchemy.orm import relationship, declarative_base, Mapped
import uuid
from typing import Optional, TYPE_CHECKING
from database.base import Base

if TYPE_CHECKING:
    from database.models.Retailer import Retailer

class CreditNoteItems(Base):
    __tablename__ = 'CreditNote_Items'
    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    credit_note_id = Column(UUID(as_uuid=True), ForeignKey('CreditNote._id'))
    credit_note = relationship("CreditNote", back_populates="credit_note_items")

class CreditNote(Base):
    __tablename__ = 'CreditNote'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cn_name = Column(String, nullable=True)
    FE_name = Column(String, nullable=True)
    feuser_id = Column(UUID(as_uuid=True), ForeignKey('FeUser._id'), nullable=True)
    retailer_id = Column(UUID(as_uuid=True), ForeignKey('Retailer._id'), nullable=True)
    deal_id = Column(UUID(as_uuid=True), ForeignKey('Deal._id'), nullable=True)
    status = Column(String, nullable=False, default="Not Picked")
    date = Column(DateTime, nullable=True)
    pickup_date = Column(DateTime, nullable=True)
    cn_items = Column(ARRAY(UUID(as_uuid=True)), nullable=True)
    is_inventory_in = Column(Boolean, nullable=False, default=False)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    retailer: Mapped[Optional["Retailer"]] = relationship('Retailer', back_populates='credit_notes')
    credit_note_items = relationship("CreditNoteItems", back_populates="credit_note")