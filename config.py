
from sqlalchemy.orm import Session 
from sqlalchemy import func
from datetime import datetime, timedelta
import uuid
from database.models.Sales import Sales


# from llm import llm


# CASE 2 
def compare_quantity_inventory_recon(data):
    recon_items = data["recon_items"]
    inventory_items = data["inventory_items"]

    for recon_item in recon_items:
        for inventory_item in inventory_items:
            if recon_item["product_id"] == inventory_item["product_id"]:
                if recon_item["quantity"] > inventory_item["quantity"]:
                    return True
                
    return False


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


def detect_sales_drop(data):  
    sales_entries = data.get("sales_entries", [])
    
    for entry in sales_entries:
        current_quantity = entry["quantity"]
        prev_quantity = entry.get("prev_quantity")
        
        if prev_quantity is not None and current_quantity < 0.8 * prev_quantity:
            return True
    
    return False
 


def check_sales_anomaly(session: Session, retailer_id: uuid.UUID, product_id: uuid.UUID, current_quantity: int, threshold: float):
    # Define time period (e.g., last 30 days)
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    # Fetch historical sales data
    historical_sales = session.query(Sales).filter(
        Sales.retailer_id == retailer_id,
        Sales.product_id == product_id,
        #Sales.date >= start_date,
        #Sales.date <= end_date
    ).all()

    print(historical_sales)

    # Flatten results
    historical_sales = [sale.quantity for sale in historical_sales]
    
    print(historical_sales)

    if len(historical_sales) == 0:
        return "No historical sales data available for this product and retailer."

    # Calculate mean and standard deviation
    avg_sales = sum(historical_sales) / len(historical_sales)
    std_sales = (sum((x - avg_sales) ** 2 for x in historical_sales) / len(historical_sales)) ** 0.5

    # Define anomaly range
    lower_bound = avg_sales - (threshold * std_sales)
    upper_bound = avg_sales + (threshold * std_sales)

    # Check for anomaly
    if current_quantity < lower_bound or current_quantity > upper_bound:
        deviation = ((current_quantity - avg_sales) / avg_sales) * 100
        return f"⚠️ Alert: Sales deviation detected! Current sales deviate by {deviation:.2f}% from historical average."
    else:
        return "✅ Sales are within normal historical range."

 
ALERT_RULES = {
    "is_retailer_shelf_image" : lambda data:is_retailer_shelf_image_event(data),
    "compare_quantity_inventory_recon" : lambda data:compare_quantity_inventory_recon(data),
    "drop_in_sales" : lambda _ :detect_sales_drop()
}