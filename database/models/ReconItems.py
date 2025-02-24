from database.db import Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column, Integer, DateTime ,ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from typing import Optional , TYPE_CHECKING
import uuid
import datetime

if TYPE_CHECKING:
    from database.models.Recon import Recon

class ReconItem(Base):
    __tablename__ = 'Recon Items'
    
    _id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recon_id = Column(PG_UUID(as_uuid=True), ForeignKey('Recon._id'), nullable=True, default=uuid.uuid4)
    product_id = Column(PG_UUID(as_uuid=True), nullable=False)
    quantity = Column(Integer, nullable=False)
    createdAt = Column(DateTime, nullable=False, default=datetime.datetime.now)
    updatedAt = Column(DateTime, nullable=False, default=datetime.datetime.now, onupdate=datetime.datetime.now)
    
    recon : Mapped[Optional["Recon"]] = relationship("Recon", back_populates="ReconItems")