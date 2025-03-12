import uuid
from database.db import db
from sqlalchemy import Date, cast
from sqlalchemy.sql import func, extract
from datetime import datetime, timedelta
from database.models.Sales import Sales
from database.models.Retailer import Retailer
from database.models.Order import Order
from database.models.DeliveryLogs import DeliveryLogs
from database.models.Warehouse import WarehouseItems
from database.models.Inventory import InventoryStockList, Inventory
from database.models.Recon import Recon
from database.models.BeatPlan import BeatPlan
from database.models.Field_Exec import Field_Exec
from database.models.RetailerVisitedLog import RetailerVisitedLog
from database.models.ASM import ASM
from database.models.CreditNote import CreditNote

# CASE 2 
def compare_quantity_inventory_recon(recon_id):
    print("Checking quantity in inventory and recon...")
    messages = []
    
    recon = db.get_session().query(Recon).filter(Recon._id == recon_id).first()
    retailer = db.get_session().query(Retailer).filter(Retailer._id == recon.retailer_id).first()
    field_exec = db.get_session().query(Field_Exec).filter(Field_Exec._id == retailer.FE_id).first()
    recepient = field_exec.Contact_Number
    
    recon_items = []
    inventory_items = []
    
    for item in recon.recon_items:
        recon_items.append({
            "product_id": str(item.product_id),
            "quantity": item.quantity,
            "product_name": item.product.name
        })
                
    inventory_stock_lists = db.get_session().query(InventoryStockList).all()
    
    for recon_item in recon_items:                 
        for inventory_item in inventory_stock_lists: 
            if(inventory_item.product_id == recon_item['product_id']):
                inventory_items.append({
                    "product_id": str(inventory_item.product_id),
                    "quantity": inventory_item.quantity
                })
                
    for recon_item in recon_items:
        for inventory_item in inventory_items:
            if recon_item["product_id"] == inventory_item["product_id"]:
                if recon_item["quantity"] > inventory_item["quantity"]:
                    messages.append({
                        "message": f"Inventory quantity for {recon_item['product_name']} is less than the recon quantity."
                    })                
    context = {
        "recepient": recepient,
        "person_name" : field_exec.Name,
        "role" : "Field Executive",
        "messages" : messages
    }
    return context

# CASE 4 
def is_retailer_shelf_image_event(recon_id):
    print("Checking if retailer shelf image is provided for the recon.")
    messages = []
    
    recon = db.get_session().query(Recon).filter(Recon._id == recon_id).first()
    retailer = db.get_session().query(Retailer).filter(Retailer._id == recon.retailer_id).first()
    field_exec = db.get_session().query(Field_Exec).filter(Field_Exec._id == retailer.FE_id).first()
    recepient = field_exec.Contact_Number
  
    quantity = sum(item.quantity for item in recon.recon_items)
    image = recon.image[0] if recon.image else ""
 
    if quantity == 0 and image == "":
        messages.append({
            "recepient": recepient,
            "message": "No quantity and image provided for the recon."
        })
    
    if quantity > 0 and image == "":
        messages.append({
            "recepient": recepient,
            "message": "No image provided for the recon."
        })
        
    if quantity == 0 and image != "":
        #response = llm.process_image_and_prompt(image)
        #return response
        messages.append({
            "message": "response"
        })
        
    context = {
        "recepient": recepient,
        "person_name" : field_exec.Name,
        "role" : "Field Executive",
        "messages" : messages
    }
    return context

# CASE 5 
def detect_sales_drop():  
    messages = []
    
    sales = db.get_session().query(Sales).all()
    
    for sale in sales:
        if sale:
            asm = db.get_session().query(ASM).filter(ASM._id == sale.retailer.asm._id).first()
            recepient = asm.Contact_Number
            
            current_quantity = sale.quantity
            prev_quantity = db.get_session().query(Sales).filter(
                Sales.retailer_id == sale.retailer_id,
                Sales.product_id == sale.product_id,
                Sales.date < sale.date
            ).order_by(Sales.date.desc()).first().quantity
            
            if prev_quantity is not None and current_quantity < 0.8 * prev_quantity:
                messages.append({
                    "recepient": recepient,
                    "message": f"Sales drop detected for {sale.product.name} at {sale.retailer.name}."
                })
    
    return messages
 
 
# CASE 3 
def check_sales_anomaly(data):
    print("Checking for sales anomaly...")
    
    retailer_id = data['retailer_id'] 
    product_id = data['product_id'] 
    current_quantity = data['quantity']
    threshold: float = 0.8
    
    messages = []
    
    start_date = datetime.now() - timedelta(days=30)
    end_date = datetime.now()
    
    retailer = db.get_session().query(Retailer).filter(Retailer._id == retailer_id).first()
    field_exec = db.get_session().query(Field_Exec).filter(Field_Exec._id == retailer.FE_id).first()
    recepient = field_exec.Contact_Number
    
    print(f"Checking sales anomaly for {retailer.name} and product {product_id} with threshold {threshold} and current quantity {current_quantity}")

    historical_sales = db.get_session().query(Sales).filter(
        Sales.retailer_id == retailer_id,
        Sales.product_id == product_id,
        Sales.date >= start_date,
        Sales.date <= end_date
    ).all()

    historical_sales = [sale.quantity for sale in historical_sales]
    
    if len(historical_sales) == 0:
        messages.append({
            "recepient": recepient,
            "message": "No historical sales data available for this product and retailer."
        })

    avg_sales = sum(historical_sales) / len(historical_sales)
    std_sales = (sum((x - avg_sales) ** 2 for x in historical_sales) / len(historical_sales)) ** 0.5

    lower_bound = avg_sales - (threshold * std_sales)
    upper_bound = avg_sales + (threshold * std_sales)

    if current_quantity < lower_bound or current_quantity > upper_bound:
        deviation = ((current_quantity - avg_sales) / avg_sales) * 100
        messages.append({
            "recepient": recepient,
            "message": f"Alert: Sales deviation detected! Current sales deviate by {deviation:.2f}% from historical average."
        })  
    else:
        messages.append({
            "recepient": recepient,
            "message": "Sales are within normal historical range."
        })
        
    return messages


# CASE 6 
def check_warehouse_inventory(MIN_STOCK_LEVEL=20):
    messages = []
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
    credit_notes = db.get_session().query(CreditNote).all()
    
    for order in orders:
        if order.status == "In-Transit":
            delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
            if delivery_log and delivery_log.delivery_person:
                recepient = delivery_log.delivery_person.Contact_Number
                message = f"Delivery for order {order.order_name} is in transit, please perform the delivery."
                
                messages.append({
                    "recepient": recepient,
                    "message": message
                })
                
    for credit_note in credit_notes:
        if credit_note.status == "In-Transit":
                delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs == order._id).first()
                if delivery_log and delivery_log.delivery_person:
                    recepient = delivery_log.delivery_person.Contact_Number
                    message = f"Delivery for credit note {credit_note.cn_name} is in transit, please perform the delivery."
                    
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
                else: 
                    messages.append({
                        "recepient": "ASM number here from order . retailer",
                        "message": f"Delivery for order {order.order_name} is out on expected date"
                    })
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
        asm = db.get_session().query(ASM).filter(ASM._id == retailer.ASM_id).first()
        stock_lists = inventory.stock_lists
        
        for stock in stock_lists:
            product = stock.product
            batch_codes = product.batch_codes
            batch_codes.sort(key=lambda x: x.expiry_date)
            
            for batch_code in batch_codes:
                expiry_date = batch_code.expiry_date
                
                if expiry_date.replace(tzinfo=None) <= datetime.now() + timedelta(days=30):
                    messages.append({
                        "recepient": asm.Contact_Number,
                        "message": f"Stock of {product.name} is expiring soon. Please take necessary action."
                    })
                    
    return messages

#CASE 20 
def check_beatplans_for_today():
    today = datetime.today().date()
    
    all_fes = db.get_session().query(Field_Exec).all()

    assigned_fes = db.get_session().query(BeatPlan.FE_id).filter(
        cast(BeatPlan.date, Date) == today 
    ).distinct().all()

    assigned_fe_ids = {fe.FE_id for fe in assigned_fes}

    missing_fes = [(fe.Name, fe.ASM_id) for fe in all_fes if fe._id not in assigned_fe_ids]
    
    grouped_by_recipient = {}
    
    for missing_fe in missing_fes:
        if missing_fe[1] is not None:
            asm = db.get_session().query(ASM).filter(ASM._id == missing_fe[1]).first()
            recipient = asm.Contact_Number
            
            if recipient not in grouped_by_recipient:
                grouped_by_recipient[recipient] = []
            grouped_by_recipient[recipient].append(missing_fe[0])
    
    fe_list = []
    for recipient, names in grouped_by_recipient.items():
        names_str = ", ".join(names)
        message = f"BeatPlan not assigned to {names_str} for today."
        fe_list.append({
            "recipient": recipient,
            "message": message
        })
    
    return fe_list

# CASE 23
def check_retailer_visits_for_month():
    """Checks which retailers have been visited less than 4 times in the current month."""
    current_year = datetime.today().year
    current_month = datetime.today().month

    low_visit_retailers = db.get_session().query(
        RetailerVisitedLog.retailer_id,
        RetailerVisitedLog.fe_id,
        Retailer.name.label("retailer_name"),
        Field_Exec.Name.label("fe_name"),
        ASM.Contact_Number.label("asm_phone_number"),
        func.count(RetailerVisitedLog._id).label("visit_count")
    ).join(
        Retailer, Retailer._id == RetailerVisitedLog.retailer_id
    ).join(
        Field_Exec, Field_Exec._id == RetailerVisitedLog.fe_id
    ).join(
        ASM, ASM._id == Retailer.ASM_id
    ).filter(
        extract("year", RetailerVisitedLog.lastVisited) == current_year,
        extract("month", RetailerVisitedLog.lastVisited) == current_month
    ).group_by(
        RetailerVisitedLog.retailer_id,
        RetailerVisitedLog.fe_id,
        Retailer.name,
        Field_Exec.Name,
        ASM.Contact_Number
    ).having(
        func.count(RetailerVisitedLog._id) < 4
    ).all()

    grouped_by_recipient = {}
    
    for visit in low_visit_retailers:
        recipient = visit.asm_phone_number
        retailer_info = f"{visit.retailer_name} (FE: {visit.fe_name})"

        if recipient not in grouped_by_recipient:
            grouped_by_recipient[recipient] = []
        grouped_by_recipient[recipient].append(retailer_info)
    
    retailer_list = []
    for recipient, names in grouped_by_recipient.items():
        names_str = ", ".join(names)
        message = f"These retailers were visited less than 4 times this month: {names_str}."
        retailer_list.append({
            "recipient": recipient,
            "message": message
        })
    return retailer_list


# CASE 14 
def expiring_products():
        
    messages = [] 
    inventory_stocks = db.get_session().query(InventoryStockList).all()
    
    for stock in inventory_stocks:
        if stock.inventory and stock.product:
            retailer = stock.inventory.retailer
            product = stock.product
            
            if retailer:    
                sorted_batches = sorted(stock.product.batch_codes, key=lambda batch: batch.expiry_date)
                
                for batch in sorted_batches:
                    expiry_date = batch.expiry_date
                    days_left = (expiry_date.replace(tzinfo=None) - datetime.now()).days
                    
                    if days_left > 0 and days_left <= 30: 
                        messages.append({
                            "recepient" : retailer.asm.Contact_Number,
                            "message" : f"Product: {product.name}, Expiry Date: {expiry_date}, Days Left: {days_left}"
                        })        
                        
    return messages


event_config = {
    "recon_inserted" : [
        lambda recon_id : compare_quantity_inventory_recon(recon_id),
        lambda recon_id : is_retailer_shelf_image_event(recon_id)
    ],
    "sudden_sales_drop" : [
        lambda x : detect_sales_drop(),
        lambda x : check_sales_anomaly(x)
    ],
    "low_retailer_visits" : [
        lambda x : check_retailer_visits_for_month(),    
    ],
    "daily_event_triggers" : [
        lambda x : notify_delivery_for_orders(),
        lambda x : delivery_not_out_on_expected_date(),
        lambda x : nearly_expiring_stocks(),
        lambda x : check_beatplans_for_today(),
        lambda x : expiring_products(),
        
    ]
}