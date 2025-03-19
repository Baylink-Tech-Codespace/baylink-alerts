from sqlalchemy import Column, DateTime, ForeignKey, func, UUID
from sqlalchemy.orm import relationship, Mapped
from typing import Optional
import uuid

from database.base import Base
from database.models.Field_Exec import Field_Exec
from database.models.Retailer import Retailer

class RetailerVisitedLog(Base):
    __tablename__ = "RetailerVisitedLog"

    _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    fe_id = Column(UUID(as_uuid=True), ForeignKey("Field_Exec._id"), nullable=False, comment="Field Executive ID")
    retailer_id = Column(UUID(as_uuid=True), ForeignKey("Retailer._id"), nullable=False, comment="Retailer ID")
    lastVisited = Column(DateTime, nullable=True, comment="Last visit timestamp")
    visit_start = Column(DateTime, nullable=True, comment="visit start timestamp")
    visit_end = Column(DateTime, nullable=True, comment="visit end timestamp")
    createdAt = Column(DateTime, nullable=False, server_default=func.now(), comment="Record creation timestamp")
    updatedAt = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update timestamp")

    #field_exec = relationship("Field_Exec", back_populates="retailer_visits")
    #retailer = relationship("Retailer", back_populates="visit_logs")

#Field_Exec.retailer_visits = relationship("RetailerVisitedLog", back_populates="field_exec")
#Retailer.visit_logs = relationship("RetailerVisitedLog", back_populates="retailer")
