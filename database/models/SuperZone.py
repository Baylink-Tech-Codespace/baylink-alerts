
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped
from database.main import Base
from database.models.ASM import ASM
from typing import List 
import uuid

class SuperZone(Base):
    __tablename__ = 'super_zone'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    location = Column(String, nullable=True, default=None)
    warehouse_id = Column(PGUUID(as_uuid=True), ForeignKey('Warehouse._id'), nullable=False)
    
    asms : Mapped[List["ASM"]] = relationship(ASM, back_populates='super_zone') 