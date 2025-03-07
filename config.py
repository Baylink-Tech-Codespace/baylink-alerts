from sqlalchemy.orm import Session 
from sqlalchemy import Date, cast
from sqlalchemy.sql import func, extract
from datetime import datetime, timedelta
import uuid
from database.models.Sales import Sales
from database.models.Retailer import Retailer
from database.models.Order import Order
from database.db import db
from database.models.DeliveryLogs import DeliveryLogs
from database.models.WarehouseItems import WarehouseItems
from database.models.Inventory import InventoryStockList, Inventory
from database.models.Recon import Recon
from database.models.BeatPlan import BeatPlan
from database.models.Field_Exec import Field_Exec
from database.models.RetailerVisitedLog import RetailerVisitedLog

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
 
 
# CASE 3 
def check_sales_anomaly(session: Session, retailer_id: uuid.UUID, product_id: uuid.UUID, current_quantity: int, threshold: float):
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()

    # Fetch historical sales data
    historical_sales = session.query(Sales).filter(
        Sales.retailer_id == retailer_id,
        Sales.product_id == product_id,
        Sales.date >= start_date,
        Sales.date <= end_date
    ).all()

    historical_sales = [sale.quantity for sale in historical_sales]
    
    if len(historical_sales) == 0:
        return "No historical sales data available for this product and retailer."

    avg_sales = sum(historical_sales) / len(historical_sales)
    std_sales = (sum((x - avg_sales) ** 2 for x in historical_sales) / len(historical_sales)) ** 0.5

    lower_bound = avg_sales - (threshold * std_sales)
    upper_bound = avg_sales + (threshold * std_sales)

    if current_quantity < lower_bound or current_quantity > upper_bound:
        deviation = ((current_quantity - avg_sales) / avg_sales) * 100
        return f"⚠️ Alert: Sales deviation detected! Current sales deviate by {deviation:.2f}% from historical average."
    else:
        return "✅ Sales are within normal historical range."


# CASE 6 
def check_warehouse_inventory(MIN_STOCK_LEVEL=20):
    warehouse_items = db.get_session().query(WarehouseItems).all()
    
    items = []
    
    for item in warehouse_items:
        if item.quantity < MIN_STOCK_LEVEL:
            items.append(item)
    
    return items


# CASE 8
def notify_delivery_for_orders():
    messages = []
    orders = db.get_session().query(Order).all()
    
    # PERFORM SAVE FOR CN 

    for order in orders:
        if order.status == "In-Transit":
            delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
            if delivery_log:
                recepient = delivery_log.delivery_person.Contact_Number
                message = f"Delivery for order {order.order_name} is in transit, please perform the delivery."
                
                messages.append({
                    "recepient": recepient,
                    "message": message
                })            

    return messages


# CASE 9 
def delivery_not_out_on_expected_date():
    
    messages = []
    
    orders = db.get_session().query(Order).all()
    
    for order in orders:
        if order.status == "In-Transit" or order.status == "Scheduled":
            delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
            if delivery_log:
                delivery_date = delivery_log.date_of_delivery
                expected_delivery_date = order.expected_delivery_date
                
                if delivery_date != expected_delivery_date:
                    messages.append({
                        "recepient": "ASM number here from order . retailer",
                        "message": f"Delivery for order {order.order_name} is not out on expected date"
                    })
                else: return False
            else:
                messages.append({
                    "recepient": "ASM number here from order . retailer",
                    "message": f"Delivery for order {order.order_name} is not out on expected date"
                }) 
                
    return messages


# CASE 13 
def nearly_expiring_stocks():
    messages = []
    
    inventories = db.get_session().query(Inventory).all()
    
    for inventory in inventories:
        retailer = inventory.retailer
        stock_lists = inventory.stock_lists
        
        for stock in stock_lists:
            product = stock.product
            batch_codes = product.batch_codes
            batch_codes.sort(key=lambda x: x.expiry_date)
            
            for batch_code in batch_codes:
                expiry_date = batch_code.expiry_date
                
                if expiry_date <= datetime.now() + timedelta(days=30):
                    messages.append({
                        "recepient": "retailer.ASM.number",
                        "message": f"Stock of {product.name} is expiring soon. Please take necessary action."
                    })
                    
    return messages

#CASE 20
def check_beatplans_for_today(session: Session):
    today = datetime.today().date()
    
    all_fes = db.get_session().query(Field_Exec._id, Field_Exec.Name).all()

    assigned_fes = db.get_session().query(BeatPlan.FE_id).filter(
        cast(BeatPlan.date, Date) == today 
    ).distinct().all()

    assigned_fe_ids = {fe.FE_id for fe in assigned_fes} 

    missing_fes = [(fe._id, fe.Name) for fe in all_fes if fe._id not in assigned_fe_ids]

    if missing_fes:
        print(missing_fes)
        return {
            "alert": "BeatPlan not assigned to the following FEs:",
            "missing_fes": missing_fes
        }
    else:
        return {"message": "All FEs have a BeatPlan assigned for today."}

# CASE 23
def check_retailer_visits_for_month(session: Session):
    """Checks which retailers have been visited less than 4 times in the current month."""
    current_year = datetime.today().year
    # current_month = datetime.today().month

    current_month = 2


    low_visit_retailers = db.get_session().query(
        RetailerVisitedLog.retailer_id, 
        func.count(RetailerVisitedLog._id).label("visit_count")
    ).filter(
        extract("year", RetailerVisitedLog.lastVisited) == current_year,
        extract("month", RetailerVisitedLog.lastVisited) == current_month
    ).group_by(
        RetailerVisitedLog.retailer_id
    ).having(
        func.count(RetailerVisitedLog._id) < 4
    ).all()

    if low_visit_retailers:
        print("ALERT: Some retailers were visited fewer than 4 times this month.", low_visit_retailers)
        return {"alert": "Low visit retailers detected", "data": low_visit_retailers}
    
    return {"message": "All retailers have been visited sufficiently."}

    
    
ALERT_RULES = {
    
}