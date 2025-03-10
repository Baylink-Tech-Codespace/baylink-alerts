from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, String, ForeignKey, Boolean, Enum, DateTime, func
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship
from database.db import Base
import uuid
from sqlalchemy.orm import Mapped
from typing import Optional
from database.models.ASM import ASM

class FeUser(Base):
    __tablename__ = 'FeUsers'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fe_id = Column(PGUUID(as_uuid=True), ForeignKey('Field_Exec._id'), nullable=True)
    isLoggedIn = Column(Boolean, nullable=True)
    
    role = Column(Enum(
        'Field_Exec', 'Admin', 'Warehouse_Manager', 'Delivery_Person', 'ASM', 'Promoter', 'DB_Admin',
        name='role_enum'
    ), nullable=False, default='Field_Exec')
    
    OTP = Column(String, nullable=True)
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    Field_Exec : Mapped[Optional["Field_Exec"]] = relationship('Field_Exec', back_populates='feuser')

class Field_Exec(Base):
    __tablename__ = 'Field_Exec'

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    zone_id = Column(PGUUID(as_uuid=True), nullable=True)
    ASM_id = Column(PGUUID(as_uuid=True), ForeignKey('ASM._id'), nullable=True)
    Name = Column(String, nullable=False)
    Contact_Number = Column(String, nullable=False)
    Image = Column(String, nullable=True)
    
    #asm: Mapped[Optional["ASM"]] = relationship('ASM', back_populates='field_exec')
    feuser: Mapped[Optional["FeUser"]] = relationship('FeUser', back_populates='Field_Exec')