from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship , Mapped
from typing import Optional, TYPE_CHECKING
from database.base import Base
import uuid

if TYPE_CHECKING:
    from database.models.SuperZone import SuperZone
    from database.models.Field_Exec import Field_Exec

class ASM(Base):
    __tablename__ = 'ASMs'  

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    super_zone_id = Column(PGUUID(as_uuid=True), ForeignKey('super_zone._id'), nullable=True)
    name = Column(String, nullable=False)
    Image = Column(String, nullable=True)   
    Contact_Number = Column(String, nullable=False)  
        
    #field_exec: Mapped[Optional["Field_Exec"]] = relationship('Field_Exec', back_populates='asm')
    super_zone: Mapped[Optional["SuperZone"]] = relationship('SuperZone', back_populates='asms')
