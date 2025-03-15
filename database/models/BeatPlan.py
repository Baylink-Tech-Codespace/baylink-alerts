from sqlalchemy import Column, Date, JSON, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, Mapped
from typing import Optional, List
import uuid

from database.base import Base
from database.models.Field_Exec import Field_Exec
from database.models.Task import Task


class BeatPlan(Base):
    __tablename__ = "BeatPlan"

    _id: Mapped[uuid.UUID] = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    FE_id: Mapped[Optional[uuid.UUID]] = Column(PGUUID(as_uuid=True), ForeignKey("Field_Exec._id"), nullable=True, comment="Field Executive ID")
    date: Mapped[str] = Column(Date, nullable=False)
    plan: Mapped[List[uuid.UUID]] = Column(JSON, nullable=False, comment="Ordered list of retailer IDs for the beat plan")
    details: Mapped[Optional[dict]] = Column(JSON, nullable=True, comment="Any additional details for the beat plan")
    createdAt: Mapped[str] = Column(Date, nullable=False, server_default=func.now())
    updatedAt: Mapped[str] = Column(Date, nullable=False, server_default=func.now(), onupdate=func.now())

    field_exec = relationship("Field_Exec", back_populates="beat_plans")
    tasks = relationship("Task", back_populates="beat_plan")


Field_Exec.beat_plans = relationship("BeatPlan", back_populates="field_exec")
Task.beat_plan = relationship("BeatPlan", back_populates="tasks")
