from database.db import Base
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import Column, String, Date, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy import ForeignKey
from typing import List,Optional ,TYPE_CHECKING
import uuid

from database.models.ReconItems import ReconItem
if TYPE_CHECKING:
    from database.models.Retailer import Retailer
 
class Recon(Base):
    __tablename__ = 'Recon'
    
    _id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    retailer_id = Column(PG_UUID(as_uuid=True), ForeignKey('Retailer._id') ,nullable=False)
    deal_id = Column(PG_UUID(as_uuid=True), nullable=False)
    recon_date = Column(Date, nullable=False)
    recon_items = Column(JSON, nullable=False)  
    image = Column(ARRAY(String), nullable=False, default=[])
    merchandising_images = Column(ARRAY(String), nullable=True, default=[])
    updated_by = Column(String, nullable=False)
    
    ReconItems : Mapped[List["ReconItem"]] = relationship("ReconItem", back_populates="recon")
    # Retailer: Mapped[Optional["Retailer"]] = relationship("Retailer", back_populates="Recon")