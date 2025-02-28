
# from llm import llm



# CASE 4 
def is_retailer_shelf_image_event(data):
    image = data["image_url"]
    quantity = data["quantity"]
 
    if quantity == 0 and image == "":
        return False
    
    if quantity > 0 and image == "":
        return True
    
    if quantity == 0 and image != "":
        
        #response = llm.process_image_and_prompt(image)
        #return response
        return True
 

# CASE 2 
def compare_quantity_inventory_recon(data):
    quantity = data["quantity"]
    if quantity > 0:
        return True
    else:
        return False
 
ALERT_RULES = {
    "is_retailer_shelf_image" : lambda data:is_retailer_shelf_image_event(data),
    "compare_quantity_inventory_recon" : lambda data:compare_quantity_inventory_recon(data)
}