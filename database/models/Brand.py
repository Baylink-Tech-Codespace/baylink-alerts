from sqlalchemy import Column, String, Integer, ForeignKey, DateTime, UUID, func
from sqlalchemy.orm import relationship, Mapped
import uuid
from datetime import datetime
from database import Base
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from database.models.Product import Product

class Brand(Base):
    __tablename__ = 'Brands'

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False, unique=True)
    contact_person = Column(String, nullable=False)
    email = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    GSTIN = Column(String, nullable=True)
    image = Column(String, nullable=True)
    banner_image = Column(String, nullable=True)
    threshold = Column(Integer, nullable=False, default=4000)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    product : Mapped[List["Product"]] = relationship("Product", back_populates="brand")
