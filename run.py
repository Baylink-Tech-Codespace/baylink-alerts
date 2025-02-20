from database.main import db
from database.models.ASM import ASM 
from database.models.SuperZone import SuperZone
from database.models.Retailer import Retailer
from database.models.Recon import Recon
 
retailers = db.get_session().query(Retailer).all() 
recons = db.get_session().query(Recon).all()

for recon in recons:
    print(recon.Retailer.name)
    
for retailer in retailers:
    for recon in retailer.Recon:
        print(recon.image)