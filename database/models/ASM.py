from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship , Mapped
from typing import Optional, TYPE_CHECKING
from database.base import Base
import uuid

if TYPE_CHECKING:
    from database.models.SuperZone import SuperZone

class ASM(Base):
    __tablename__ = 'ASMs'  

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    super_zone_id = Column(PGUUID(as_uuid=True), ForeignKey('super_zone._id'), nullable=True)
    name = Column(String, nullable=False)
    Image = Column(String, nullable=True)   
    Contact_Number = Column(String, nullable=False)  
    ASM_id = Column(PGUUID(as_uuid=True), ForeignKey('asm._id'), nullable=True)  

    super_zone: Mapped[Optional["SuperZone"]] = relationship('SuperZone', back_populates='asms')
