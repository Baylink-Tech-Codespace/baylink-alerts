 
from database.main import db
from database.models.ASM import ASM 
from database.models.SuperZone import SuperZone
from database.models.Retailer import Retailer
from database.models.Recon import Recon
 
def get_test_event() -> dict:
    event_type = "is_retailer_shelf_image"
    
    asms = db.get_session().query(ASM).all() 
    
    asm_ids = []
    
    for asm in asms:
        if asm._id:
            asm_ids.append(asm._id)
            
    asm_id = asm_ids[0]
    
    retailers = db.get_session().query(Retailer).filter(Retailer.ASM_id == asm_id).all()
    recon_list = []
    
    for retailer in retailers:
        recon = db.get_session().query(Recon).filter(Recon.retailer_id == retailer._id).all()
        if recon: 
                recon_list.append(recon)
        
    test_recon = recon_list[0][0]
    quantity = 0
    image = "" if len(test_recon.image) == 0 else test_recon.image[0]
    
    for recon_item in test_recon.ReconItems:
        quantity += recon_item.quantity
 
    event_data = { 
        "image_url": image,
        "quantity": quantity   
    }

    return {
        "event_name": event_type,
        "event_data": event_data
    } 
