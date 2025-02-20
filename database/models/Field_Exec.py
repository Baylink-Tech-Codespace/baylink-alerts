from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from database.main import Base
import uuid


class Field_Exec(Base):
    __tablename__ = 'Field_Exec'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(PGUUID(as_uuid=True), nullable=True)
    #ASM_id = Column(PGUUID(as_uuid=True), ForeignKey('ASM._id'), nullable=True)
    Name = Column(String, nullable=False)
    Contact_Number = Column(String, nullable=False)
    Image = Column(String, nullable=True)
    
    #asm = relationship('ASM', back_populates='field_execs')