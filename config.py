import re
from collections import defaultdict
import uuid
import requests
import statistics
from database.db import db
from sqlalchemy import Date, and_, cast, join
from sqlalchemy.sql import func, extract
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from helper.s3 import get_recon_image_from_s3
from database.models.Brand import Brand
from database.models.Product import Product
from database.models.Sales import Sales
from database.models.Retailer import Retailer
from database.models.Order import Order, OrderItem
from database.models.DeliveryLogs import DeliveryLogs
from database.models.Task import Task
from database.models.Warehouse import WarehouseItems
from database.models.Inventory import InventoryStockList, Inventory
from database.models.Product import Product
from database.models.Recon import Recon
from database.models.BeatPlan import BeatPlan
from database.models.Field_Exec import Field_Exec
from database.models.RetailerVisitedLog import RetailerVisitedLog
from database.models.ASM import ASM
from database.models.CreditNote import CreditNote
from collections import defaultdict

from constants import SWIPE_DOC_API_URL, SWIPE_TOKEN
from shelf_classification.main import is_shelf_image

#CASE 1
def fetch_retailer_transactions(retailer_id, start_date, end_date, payment_status):
    try:
        """Fetch transactions for a specific retailer from the API. Only check once in a month"""
        HEADERS = {
        "Authorization": f"Bearer {SWIPE_TOKEN}"
        }
        querystring = {
            "document_type": "invoice",
            "start_date": start_date,
            "end_date": end_date,
            "payment_status": payment_status,
            "customer_id": retailer_id,
        }

        response = requests.request("GET", SWIPE_DOC_API_URL, headers=HEADERS, params=querystring)
        
        data = response.json()

        if response.status_code == 200:
            if data['data']['transactions'] is None: 
                return []
            return data["data"]["transactions"]
        else:
            print("Failed to fetch transactions")
            return []
        
    except Exception as e:
        print(f"Failed to fetch transactions: {e}")
        return []

# CASE 1 

def check_all_retailers_pending_bills():
    try:
        print("Checking for retailers if they have more than two pending bills")
        alerts = []

        start_date = "01-09-2024"
        end_date = (datetime.now() - timedelta(days=60)).strftime("%d-%m-%Y")

        retailers = db.get_session().query(Retailer).all()

        alerts_dict = {}

        for retailer in retailers:
            field_exec = db.get_session().query(Field_Exec).filter(Field_Exec._id == retailer.FE_id).first()
            payment_status = "pending"

            pending_transactions = fetch_retailer_transactions(retailer._id, start_date, end_date, payment_status)
            
            if len(pending_transactions) > 2: 
                recipient = field_exec.Contact_Number
                retailer_name = retailer.name
                person_name = field_exec.Name
                role = "Field Executive"

                if recipient not in alerts_dict:
                    alerts_dict[recipient] = {
                        "retailers": [],
                        "person_name": person_name,
                        "role": role
                    }

                alerts_dict[recipient]["retailers"].append(retailer_name)

        alerts = []
        
        for recipient, data in alerts_dict.items():
            message = f"Retailers {', '.join(data['retailers'])} have more than 2 pending bills."

            alerts.append({
                "recipient": recipient,
                "message": message,
                "person_name": data["person_name"],
                "role": data["role"]
            })

        return alerts
    
    except Exception as e:
        print(f"Failed to check retailers pending bills: {e}")
        return []

# CASE 2 
def compare_quantity_inventory_recon(recon_id):
    try:
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

    except Exception as e:
        print(f"Failed to check quantity in inventory and recon: {e}")
        return []
    
# CASE 4 
def is_retailer_shelf_image_event(recon_id):
    try:
        print("Checking if retailer shelf image is provided for the recon.")
        message = ""
        
        recon = db.get_session().query(Recon).filter(Recon._id == recon_id).first()
        retailer = db.get_session().query(Retailer).filter(Retailer._id == recon.retailer_id).first()
        field_exec = db.get_session().query(Field_Exec).filter(Field_Exec._id == retailer.FE_id).first()
        recepient = field_exec.Contact_Number
    
        quantity = sum(item.quantity for item in recon.recon_items)
        image = recon.image[0] if recon.image else ""
        
        s3_image_url = get_recon_image_from_s3(image)
        shelf_image = is_shelf_image(s3_image_url)
        
        if quantity == 0 and image == "":
            message = "No quantity and image provided for the recon."
        
        if quantity > 0 and image == "":
            message = "No image provided for the recon."
            
        if quantity == 0 and image != "" and shelf_image == False: 
            message = "Shelf Image not provided for the recon."
            
        context = {
            "recepient": recepient,
            "person_name" : field_exec.Name,
            "role" : "Field Executive",
            "messages" : [message]
        }
        return context
    
    except Exception as e:
        print(f"Failed to check if retailer shelf image is provided for the recon: {e}")
        return []

# CASE 5 
def detect_sales_drop():  
    try:
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
                        "message": f"Sales drop detected for {sale.product.name} at {sale.retailer.name}.",
                        "person_name" : asm.name,
                        "role" : "ASM"
                    })
        
        return messages
    
    except Exception as e:
        print(f"Failed to detect sales drop: {e}")
        return []
 
# CASE 3 
def check_sales_anomaly(data):
    try:
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
                "message": "No historical sales data available for this product and retailer.",
                "person_name" : field_exec.Name,
                "role" : "Field Executive"
            })

        avg_sales = sum(historical_sales) / len(historical_sales)
        std_sales = (sum((x - avg_sales) ** 2 for x in historical_sales) / len(historical_sales)) ** 0.5

        lower_bound = avg_sales - (threshold * std_sales)
        upper_bound = avg_sales + (threshold * std_sales)

        if current_quantity < lower_bound or current_quantity > upper_bound:
            deviation = ((current_quantity - avg_sales) / avg_sales) * 100
            messages.append({
                "recepient": recepient,
                "message": f"Alert: Sales deviation detected! Current sales deviate by {deviation:.2f}% from historical average.",
                "person_name" : field_exec.Name,
                "role" : "Field Executive"
            })  
        else:
            messages.append({
                "recepient": recepient,
                "message": "Sales are within normal historical range.",
                "person_name" : field_exec.Name,
                "role" : "Field Executive"
            })
            
        return messages
    
    except Exception as e:
        print(f"Failed to check sales anomaly: {e}")
        return []


# CASE 6 
def check_warehouse_inventory(MIN_STOCK_LEVEL=200):
    try:
        messages = []
        warehouse_items = db.get_session().query(WarehouseItems).all()
        items = []
        
        for item in warehouse_items:
            if item.warehouse.warehouse_manager:
                if item.quantity < MIN_STOCK_LEVEL:
                    items.append({
                        "product_name" : item.product.name,
                        "quantity" : item.quantity,
                        "recepient" : item.warehouse.warehouse_manager.fe_user.Field_Exec.Contact_Number
                    })            
        
        for item in items:
            message = f"Alert: Warehouse inventory for {item['product_name']} is below the minimum stock level of {MIN_STOCK_LEVEL}. Current quantity: {item['quantity']}"
            messages.append({
                "recepient": item["recepient"],
                "message": message,
                "person_name" : item["recepient"],
                "role" : "Warehouse Manager"
            })
        
        return messages
    
    except Exception as e:
        print("Error caused at Check Warehouse Inventory: ", e)

# case 7
# Notify the warehouse manager to verify pending order deliveries and credit notes.
def notify_pending_orders():
    try: 
        print("Checking for pending order deliveries and credit notes...")

        messages = []
        today = datetime.now().date()
        
        orders = db.get_session().query(Order).filter(Order.expected_delivery_date == today).all()
        credit_notes = db.get_session().query(CreditNote).filter(CreditNote.pickup_date == today).all()
        
        for order in orders:
            if order.status == "In-Transit" or order.status == "Scheduled": 
                delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
                if delivery_log and delivery_log.delivery_person:
                    recepient = delivery_log.delivery_person.Contact_Number
                    person_name = delivery_log.delivery_person.Name
                    message =  order.order_name 
                    
                    messages.append({
                        "recepient": recepient,
                        "message": message,
                        "person_name": person_name,
                        "role": "Delivery Person"
                    })
                    
        for credit_note in credit_notes:
            if credit_note.status == "In-Transit" or credit_note.status == "Scheduled":
                delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.credit_note_id == credit_note._id).first()
                if delivery_log and delivery_log.delivery_person:
                    recepient = delivery_log.delivery_person.Contact_Number
                    person_name = delivery_log.delivery_person.Name
                    message = credit_note.credit_note_name
                    
                    messages.append({
                        "recepient": recepient,
                        "message": message,
                        "person_name": person_name,
                        "role": "Delivery Person"
                    })
                    
        grouped_messages = {}
        for message in messages:
            if message["recepient"] not in grouped_messages:
                grouped_messages[message["recepient"]] = {
                    "recepient": message["recepient"],
                    "messages": [message["message"]],
                    "person_name": message["person_name"],
                    "role": message["role"]
                }
            else:
                grouped_messages[message["recepient"]]["messages"].append(message["message"])

        for recepient, data in grouped_messages.items():
            messages = data["messages"]
            person_name = data["person_name"]
            role = data["role"]
            message = "\n".join(messages)
            
            messages.append({
                "recepient": recepient,
                "message": f"Pending order deliveries and credit notes for today:\n{message}",
                "person_name": person_name,
                "role": role
            })
            
        return messages
    except Exception as e:
        print("Error in notify Pending Orders",e)
        return []

# CASE 8
def notify_delivery_for_orders():
    try :    
        print("Checking for delivery for orders...")
        messages = []
        orders = db.get_session().query(Order).all()
        credit_notes = db.get_session().query(CreditNote).all()
        
        for order in orders:
            if order.status == "In-Transit":
                delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
                if delivery_log and delivery_log.delivery_person:
                    recepient = delivery_log.delivery_person.Contact_Number
                    person_name = delivery_log.delivery_person.Name
                    message = f"Delivery for order {order.order_name} is in transit, please perform the delivery."
                    
                    messages.append({
                        "recepient": recepient,
                        "message": message,
                        "person_name": person_name,
                        "role": "Delivery Person"
                    })
                    
        for credit_note in credit_notes:
            if credit_note.status == "In-Transit":
                    delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs == order._id).first()
                    if delivery_log and delivery_log.delivery_person:
                        recepient = delivery_log.delivery_person.Contact_Number
                        person_name = delivery_log.delivery_person.Name 
                        message = f"Delivery for credit note {credit_note.cn_name} is in transit, please perform the delivery."
                        
                        messages.append({
                            "recepient": recepient,
                            "message": message,
                            "person_name": person_name,
                            "role": "Delivery Person"
                    }) 
                        
        return messages
        
    except Exception as e:
        print(f"Error in notify_delivery_for_orders: {e}")
        return []

# CASE 9 
def delivery_not_out_on_expected_date():
    try :
        print("Checking for delivery not out on expected date...")
        messages = []
        orders = db.get_session().query(Order).all()
        
        for order in orders:
            if order.status == "In-Transit" or order.status == "Scheduled":
                delivery_log = db.get_session().query(DeliveryLogs).filter(DeliveryLogs.order_id == order._id).first()
                if delivery_log and delivery_log.delivery_person:
                    recepient = delivery_log.delivery_person.Contact_Number

                    if delivery_log:
                        delivery_date = delivery_log.date_of_delivery
                        expected_delivery_date = order.expected_delivery_date
                        
                        if delivery_date != expected_delivery_date:
                            messages.append({
                                "recepient": recepient,
                                "message": f"Delivery for order {order.order_name} is not out on expected date",
                                "role" : "Delivery Person",
                                "person_name" : delivery_log.delivery_person.Name
                            })
                        else: 
                            messages.append({
                                "recepient": recepient,
                                "message": f"Delivery for order {order.order_name} is out on expected date",
                                "role" : "Delivery Person",
                                "person_name" : delivery_log.delivery_person.Name
                            })
                    else:
                        messages.append({
                            "recepient": recepient,
                            "message": f"Delivery for order {order.order_name} is not out on expected date",
                            "role" : "Delivery Person",
                            "person_name" : delivery_log.delivery_person.Name
                        }) 
                                        
        return messages
    
    except Exception as e:
        print(f"Error in delivery_not_out_on_expected_date: {e}")
        return []


# CASE 13
def nearly_expiring_stocks():
    try:
        print("Checking for nearly expiring stocks...")
        messages = []
        inventories = db.get_session().query(Inventory).all()
        
        for inventory in inventories:
            retailer = inventory.retailer
            asm = db.get_session().query(ASM).filter(ASM._id == retailer.ASM_id).first()
            person_name = asm.name
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
                            "message": f"Stock of {product.name} is expiring soon. Please take necessary action.",
                            "person_name" : person_name,
                            "role" : "ASM"
                        })
                            
        return messages
    
    except Exception as e:
        print(f"Error in nearly_expiring_stocks: {e}")
        return []

# CASE 18
def check_skipped_orders_alert():
    try:
        print("Checking if a retailer is skipping giving orders on every beat plan for last 3 weeks.")
        messages = []
        today = datetime.today().date()
        last_three_weeks = today - timedelta(weeks=3)

        recent_beatplans = db.get_session().query(BeatPlan._id, BeatPlan.plan).filter(
            cast(BeatPlan.date, Date) >= last_three_weeks
        ).all()

        retailer_task_counts = {}

        beat_plan_ids = [bp._id for bp in recent_beatplans]
        retailer_task_counts = {retailer_id: {"total_tasks": 0, "skipped_orders": 0} for bp in recent_beatplans for retailer_id in bp.plan}

        total_order_tasks = db.get_session().query(Task.retailer_id, Task.status).filter(
            Task.beat_plan_id.in_(beat_plan_ids), 
            Task.type == "Order"
        ).all()

        for retailer_id, status in total_order_tasks:
            retailer_id_str = str(retailer_id) 

            if retailer_id_str in retailer_task_counts:  
                retailer_task_counts[retailer_id_str]["total_tasks"] += 1

                if status != "Completed":
                    retailer_task_counts[retailer_id_str]["skipped_orders"] += 1

        asm_retailers_map = defaultdict(lambda: {"contact": None, "retailers": [], "role": "ASM" , "person_name": ""})

        for retailer_id, counts in retailer_task_counts.items():
            if counts["total_tasks"] > 0 and counts["skipped_orders"] == counts["total_tasks"]:
                retailer = db.get_session().query(Retailer).filter(Retailer._id == retailer_id).first()
                asm = db.get_session().query(ASM).filter(ASM._id == retailer.ASM_id).first()
                asm_retailers_map[asm._id]["contact"] = asm.Contact_Number 
                asm_retailers_map[asm._id]["retailers"].append(retailer.name)
                asm_retailers_map[asm._id]["person_name"] = asm.name
                
        for asm_id, data in asm_retailers_map.items():
            if data["contact"] and data["retailers"]:
                retailer_names = ", ".join(data["retailers"])
                message = f"The following retailers have not ordered in the last 3 weeks: {retailer_names}."
                messages.append({
                    "recipient": data["contact"],
                    "message": message,
                    "role": data["role"],
                    "person_name": data["person_name"]
                })
                
        return messages
    
    except Exception as e:
        print(f"Error in check_skipped_orders_alert: {e}")
        return []


# CASE 19
def check_short_visits(data):
    try:
        retailer_id = data['retailer_id']
        fe_id = data['fe_id']
        visit_start = datetime.fromisoformat(data['visit_start'])
        visit_end = datetime.fromisoformat(data['visit_end'])

        messages = []

        if visit_start and visit_end:
            time_spent = (visit_end - visit_start).total_seconds() / 60

            if time_spent < 10:
                retailer = db.get_session().query(Retailer).filter(Retailer._id == retailer_id).first()
                
                asm = db.get_session().query(ASM).filter(ASM._id == retailer.ASM_id).first()

                fe = db.get_session().query(Field_Exec).filter(Field_Exec._id == fe_id).first()
                        
                if asm and fe:
                    messages.append({
                        "recipient": asm.Contact_Number,
                        "message": f"Short visit by {fe.Name}, spent only {time_spent:.2f} min at {retailer.name}.",
                        "person_name": asm.name,
                        "role": "ASM"
                    })
        return messages
    
    except Exception as e:    
        print(f"Error in check_short_visits: {e}")   
        return []

#CASE 20  
def check_beatplans_for_today():
    try:    
        print("Checking whether BeatPlan is assigned to every FE or not")
        messages = []

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
                person_name = asm.name
                role = "ASM"
                
                if recipient not in grouped_by_recipient:
                    grouped_by_recipient[recipient] = {
                        "names": [],
                        "person_name": person_name,
                        "role": role
                    }
                
                grouped_by_recipient[recipient]["names"].append(missing_fe[0])

        for recipient, details in grouped_by_recipient.items():
            names_str = ", ".join(details["names"])
            message = f"BeatPlan not assigned to {names_str} for today."
            messages.append({
                "recipient": recipient,
                "message": message,
                "person_name": details["person_name"],
                "role": details["role"]
            })

        return messages
    
    except Exception as e:
        print(f"Error in check_beatplans_for_today: {e}")
        return []

# CASE 23
def check_retailer_visits_for_month():
    try:
        print("Checking which retailers have been visited less than 4 times in the current month.")
        messages = []
        current_year = datetime.today().year
        current_month = datetime.today().month

        low_visit_retailers = db.get_session().query(
            RetailerVisitedLog.retailer_id,
            RetailerVisitedLog.fe_id,
            Retailer.name.label("retailer_name"),
            Field_Exec.Name.label("fe_name"),
            ASM.name,
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
            ASM.name, 
            ASM.Contact_Number
        ).having(
            func.count(RetailerVisitedLog._id) < 4
        ).all()

        grouped_by_recipient = {}
        
        for visit in low_visit_retailers:
            recipient = visit.asm_phone_number
            person_name = visit.name
            retailer_info = f"{visit.retailer_name} (FE: {visit.fe_name})"

            if recipient not in grouped_by_recipient:
                grouped_by_recipient[recipient] = {
                    "person_name": person_name,
                    "retailers": []
                }
            grouped_by_recipient[recipient]["retailers"].append(retailer_info)

        for recipient, data in grouped_by_recipient.items():
            names_str = ", ".join(data["retailers"])
            message = f"These retailers were visited less than 4 times this month: {names_str}."
            messages.append({
                "recipient": recipient,
                "message": message,
                "person_name": data["person_name"], 
                "role": "ASM",
            })

        return messages
    
    except Exception as e:
        print(f"Error in check_retailer_visits_for_month: {e}")
        return []

# CASE 24
def get_least_selling_brand_per_retailer():
    try:
        print("Finding the brand with the least sales for each retailer in the given month.")
        messages = []
        
        start_date = datetime.now() - timedelta(days=30)
        end_date = datetime.now()

        sales_query = (
            db.get_session().query(
                Sales.retailer_id,
                Retailer.name.label("retailer_name"),
                Product.brand_id,
                Brand.name.label("brand_name"),
                Product.name.label("product_name"),
                func.sum(Sales.quantity).label("total_sales"),
                ASM.Contact_Number.label("asm_contact")
            )
            .join(Retailer, Sales.retailer_id == Retailer._id)
            .join(Product, Sales.product_id == Product._id)
            .join(Brand, Product.brand_id == Brand._id) 
            .join(ASM, Retailer.ASM_id == ASM._id)
            .filter(Sales.date >= start_date, Sales.date < end_date)
            .group_by(Sales.retailer_id, Retailer.name, Product.brand_id, Brand.name, Product.name, ASM.Contact_Number)
            .subquery()
        )

        min_sales_query = (
            db.get_session().query(
                sales_query.c.retailer_id,
                sales_query.c.retailer_name,
                sales_query.c.brand_id,
                sales_query.c.brand_name,
                sales_query.c.product_name,
                sales_query.c.total_sales,
                sales_query.c.asm_contact
            )
            .order_by(sales_query.c.retailer_id, sales_query.c.total_sales)
            .distinct(sales_query.c.retailer_id)
            .all()
        )

        messages_by_recipient = defaultdict(list)

        for retailer_id, retailer_name, brand_id, brand_name, product_name, total_sales, asm_contact in min_sales_query:
            message = (
                f"Retailer '{retailer_name}' has the lowest sales in Brand '{brand_name}' "
                f"for Product '{product_name}' with {total_sales} units sold."
            )
            messages_by_recipient[asm_contact].append(message)

        messages = [
            {"recipient": recipient, "message": " ".join(messages)}
            for recipient, messages in messages_by_recipient.items()
        ]

        return messages
    
    except Exception as e:
        print(f"Error in get_least_selling_brand_per_retailer: {e}")
        return []

# CASE 26
def check_consistently_missed_retailers():
    try:
        print("Identifing retailers who have been consistently missed in BeatPlans.")

        start_date = datetime.now() - timedelta(days=30)
        beatplans = db.get_session().query(BeatPlan).filter(BeatPlan.date >= start_date).all()

        missed_retailers = {}

        for beatplan in beatplans:
            beatplan_date = beatplan.date.date()
            plan_data = beatplan.plan

            for retailer_id in plan_data:
                visited = db.get_session().query(RetailerVisitedLog).filter(
                    RetailerVisitedLog.retailer_id == retailer_id,
                    func.date(RetailerVisitedLog.lastVisited) == beatplan_date
                ).first()

                if not visited:
                    if retailer_id not in missed_retailers:
                        missed_retailers[retailer_id] = 1
                    else:
                        missed_retailers[retailer_id] += 1

        continuously_missed = [retailer_id for retailer_id, count in missed_retailers.items() if count == 2]

        grouped_by_recipient = {}
        
        retailers = db.get_session().query(Retailer._id, Retailer.name, ASM.name.label("asm_name"), ASM.Contact_Number).join(
            ASM, Retailer.ASM_id == ASM._id
        ).filter(Retailer._id.in_(continuously_missed)).all()

        for retailer_id, retailer_name, asm_name, asm_phone in retailers:
            if asm_phone not in grouped_by_recipient:
                grouped_by_recipient[asm_phone] = {
                    "person_name": asm_name, 
                    "retailers": []
                }
        
            grouped_by_recipient[asm_phone]["retailers"].append(retailer_name)

        messages = []
        for recipient, data in grouped_by_recipient.items():
            names_str = ", ".join(data["retailers"])
            message = f"These retailers were skipped in last 4 beats: {names_str}."
            
            messages.append({
                "recipient": recipient,
                "message": message,
                "person_name": data["person_name"], 
                "role": "ASM", 
            })

        return messages
    
    except Exception as e:
        print(f"Error in check_consistently_missed_retailers: {e}")
        return []


# CASE 27 
def order_limits(data):
    try:
        print("Checking the limits on order")
        order_ids = data["order_ids"]
    
        order_items = db.get_session().query(OrderItem).join(Product).filter(
            OrderItem.order_id.in_(order_ids)
        ).all()

        total_amount = sum(item.quantity * item.product.price_to_retailer for item in order_items)

        order = db.get_session().query(Order).filter(Order._id == order_ids[0]).first() 
        
        retailer_id = order.retailer_id

        retailer = db.get_session().query(Retailer).filter(Retailer._id == retailer_id).first()
        credit_score = retailer.credit_score

        messages = [] 
        if not credit_score:
            return messages
        
        fe_id = retailer.FE_id

        if 80 <= credit_score <= 100:
            order_limit = 5000
        elif 60 <= credit_score <= 79:
            order_limit = 3500  
        elif 40 <= credit_score <= 59:
            order_limit = 1500 
        else:
            order_limit = 0  

        if(order_limit < total_amount):
            fe = db.get_session().query(Field_Exec.Name, Field_Exec.Contact_Number).filter(Field_Exec._id == fe_id).first()
            fe_name, fe_contact = (fe.Name, fe.Contact_Number)

            message = (
                f"Alert: Retailer {retailer.name} placed order of Rs. {total_amount} which is above Rs. {order_limit}. "
            )
            messages.append({
                "recipient": fe_contact,
                "message": message,
                "person_name": fe_name,
                "role": "Field Executive"
            })

        return messages
    
    except Exception as e:  
        print(f"Error checking order limits: {e}")  
        return []

# CASE 14 
def expiring_products():
    try:
        print("Checking for expiring products...")    
        messages = [] 
        inventory_stocks = db.get_session().query(InventoryStockList).all()
        
        for stock in inventory_stocks:
            if stock.inventory and stock.product:
                retailer = stock.inventory.retailer
                person_name = retailer.asm.name
                product = stock.product
                            
                if retailer:    
                    sorted_batches = sorted(stock.product.batch_codes, key=lambda batch: batch.expiry_date)
                    
                    for batch in sorted_batches:
                        expiry_date = batch.expiry_date
                        days_left = (expiry_date.replace(tzinfo=None) - datetime.now()).days
                        
                        if days_left > 0 and days_left <= 30: 
                            messages.append({
                                "recepient" : retailer.asm.Contact_Number,
                                "person_name" : person_name,
                                "role" : "ASM",
                                "message" : f"Product: {product.name}, Expiry Date: {expiry_date}, Days Left: {days_left}"
                            })     
                            
        return messages
    except Exception as e:
        print(f"Error in expiring products: {e}")


# CASE 15 
def unsold_products():
    try:
        print("Checking for unsold products for all retailers ...")

        stale_days = 21
        current_date = datetime.now(timezone.utc)
        stale_threshold = current_date - timedelta(days=stale_days)

        inventories = (
            db.get_session().query(
                Inventory.retailer_id,
                Retailer.name.label("retailer_name"),
                Retailer.FE_id,
                Field_Exec.Name.label("fe_name"),
                Field_Exec.Contact_Number.label("fe_contact"),
                InventoryStockList.product_id,
                InventoryStockList.quantity,
                Product.name.label("product_name"),
                func.count(Sales._id).label("sales_count")
            )
            .join(Retailer, Inventory.retailer_id == Retailer._id)
            .join(Field_Exec, Retailer.FE_id == Field_Exec._id)
            .join(InventoryStockList, Inventory._id == InventoryStockList.inventory_id)
            .join(Product, InventoryStockList.product_id == Product._id)
            .outerjoin(Sales, and_(Product._id == Sales.product_id, Sales.date >= stale_threshold))
            .group_by(Inventory.retailer_id, Retailer.name, Retailer.FE_id, Field_Exec.Name, Field_Exec.Contact_Number, InventoryStockList.product_id, InventoryStockList.quantity, Product.name)
            .all()
        )

        messages = []

        unsold_products_list = defaultdict(lambda: {
            "retailer_name": "",
            "details": {"products": []}
        })

        for inventory in inventories:
            if inventory.sales_count == 0 and inventory.quantity > 0:
                retailer_entry = unsold_products_list[inventory.retailer_id]
                retailer_entry["retailer_id"] = inventory.retailer_id
                retailer_entry["retailer_name"] = inventory.retailer_name
                retailer_entry["details"]["products"].append({
                    "product_name": inventory.product_name,
                    "quantity": inventory.quantity
                })
        
        for retailer_id, data in unsold_products_list.items():
            fe_contact = inventories[0].fe_contact
            fe_name = inventories[0].fe_name
            
            product_details = ", ".join([f"{p['product_name']} ({p['quantity']})" for p in data["details"]["products"]])
            message = f"Alert: Retailer {data['retailer_name']} has these products remained unsold: {product_details}" 
            
            messages.append({
                "recipient": fe_contact,
                "message": message,
                "person_name": fe_name,
                "role": "Field Executive"
            })
        
        return messages
    
    except Exception as error:
        print("Error fetching unsold products list:", error)
        raise

event_config = {
    "recon_insert" : [
        lambda recon_id : compare_quantity_inventory_recon(recon_id), #  CASE 2
        lambda recon_id : is_retailer_shelf_image_event(recon_id) #  CASE 4
    ],
    "sudden_sales_drop" : [
        lambda x : detect_sales_drop(), # CASE 5
        lambda x : check_sales_anomaly(x) #  CASE 3 
    ],
    "retailer_visit_too_short": [
        lambda x : check_short_visits(x), #CASE 19
    ],
    "order_insert": [
        lambda x : order_limits(x), #CASE 27
    ],
    "daily_event_triggers" : [
        lambda x : notify_delivery_for_orders(), # CASE 8 
        lambda x : delivery_not_out_on_expected_date(), # CASE 9
        # lambda x : nearly_expiring_stocks(), # CASE 13
        lambda x : check_beatplans_for_today(), # CASE 20
       # lambda x : expiring_products(), # CASE 14
        lambda x : check_warehouse_inventory(), # CASE 6
        lambda x : check_skipped_orders_alert(), # CASE 18
        lambda x : notify_pending_orders(), # CASE 7  
    ],
    "monthly_event_triggers" : [
        lambda x : check_all_retailers_pending_bills(), #  CASE 1 
        lambda x : unsold_products(), # CASE 15
        lambda x : check_retailer_visits_for_month(), # CASE 23
        lambda x : check_consistently_missed_retailers(), #CASE 26
        lambda x : get_least_selling_brand_per_retailer() #CASE 24
    ]
}
