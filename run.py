from database.db import db
from database.models.ASM import ASM 
from database.models.SuperZone import SuperZone
from database.models.Retailer import Retailer
from database.models.Recon import Recon
 
retailers = db.get_session().query(Retailer).filter.all() 
recons = db.get_session().query(Recon).all()