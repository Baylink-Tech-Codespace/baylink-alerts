from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy import Column, ForeignKey, Enum, DateTime, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base
import uuid

class Task(Base):
    __tablename__ = "Task"

    _id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    beat_plan_id = Column(PGUUID(as_uuid=True), ForeignKey("BeatPlan._id"), nullable=False)
    retailer_id = Column(PGUUID(as_uuid=True), ForeignKey("Retailer._id"), nullable=False)

    type = Column(Enum(
        "Recon", "PaymentCollection", "Order", "CreditNote", 
        "UpdateRetailer", "UpdateFSSAI", "MarkStoreClosed", 
        name="task_type_enum"
    ), nullable=False)

    status = Column(Enum(
        "Pending", "Completed", "Skipped", 
        name="task_status_enum"
    ), nullable=False, default="Pending")

    details = Column(JSON, nullable=True)
    
    createdAt = Column(DateTime, nullable=False, default=func.now())
    updatedAt = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    retailer = relationship("Retailer", backref="tasks")
    beat_plan = relationship("BeatPlan", backref="tasks")
