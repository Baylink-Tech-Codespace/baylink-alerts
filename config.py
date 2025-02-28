
from llm import llm

async def check_image_llm(image):
    
    response = await llm.process_image_and_prompt(image,"is_retailer_shelf_image")
        
    return True

def is_retailer_shelf_image_event(data):
    image = data["image_url"]
    quantity = data["quantity"]
 
    if quantity == 0 and image == "":
        return False
    
    if quantity > 0 and image == "":
        return True
    
    if quantity == 0 and image != "":
        
        response = check_image_llm(image)
        return response
 
ALERT_RULES = {
    "pending_payment": lambda data: data["pending_days"] > 60 or data["pending_bills"] > 2,
    "low_inventory": lambda data: data["current_stock"] < data["required_stock"] * 0.3,
    "sales_drop": lambda data: data["current_sales"] < data["historical_avg_sales"] * 0.7,
    "stock_near_expiry": lambda data:is_retailer_shelf_image_event(data),
    "is_retailer_shelf_image" : lambda data:is_retailer_shelf_image_event(data),
}