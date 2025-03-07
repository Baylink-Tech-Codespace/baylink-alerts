from sqlalchemy import Column, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped
from typing import Optional
import uuid

from database.base import Base
from database.models.Field_Exec import Field_Exec
from database.models.Retailer import Retailer

class RetailerVisitedLog(Base):
    __tablename__ = "RetailerVisitedLog"

    _id: Mapped[uuid.UUID] = Column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fe_id: Mapped[uuid.UUID] = Column(
        PGUUID(as_uuid=True), ForeignKey("Field_Exec._id"), nullable=False, comment="Field Executive ID"
    )
    retailer_id: Mapped[uuid.UUID] = Column(
        PGUUID(as_uuid=True), ForeignKey("Retailer._id"), nullable=False, comment="Retailer ID"
    )
    lastVisited: Mapped[Optional[DateTime]] = Column(
        DateTime, nullable=True, comment="Last visit timestamp"
    )
    created_at: Mapped[DateTime] = Column(
        DateTime, nullable=False, server_default=func.now(), comment="Record creation timestamp"
    )
    updated_at: Mapped[DateTime] = Column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now(), comment="Last update timestamp"
    )

    field_exec = relationship("Field_Exec", back_populates="retailer_visits")
    retailer = relationship("Retailer", back_populates="visit_logs")

Field_Exec.retailer_visits = relationship("RetailerVisitedLog", back_populates="field_exec")
Retailer.visit_logs = relationship("RetailerVisitedLog", back_populates="retailer")
