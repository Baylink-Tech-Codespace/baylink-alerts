from database.db import db
from database.models.ASM import ASM 
from database.models.SuperZone import SuperZone
from database.models.Retailer import Retailer
from database.models.Recon import Recon
from database.models.Inventory import Inventory
from database.models.Inventory import InventoryStockList
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.models.Sales import Sales
from database.models.WarehouseItems import WarehouseItems, Warehouse
from database.models.DeliveryPerson import Delivery
from database.models.DeliveryLogs import DeliveryLogs
from database.models.Order import Order

#retailers = db.get_session().query(Retailer).all() 
#recons = db.get_session().query(Recon).all()

#logs = db.get_session().query(BaylinkAlertLogs).all()

#for log in logs:
 #   print(log.data,log.message , log.message_type)


# inventories = db.get_session().query(Inventory).all()
#inventory_stock_lists = db.get_session().query(InventoryStockList).all()

#for _inventory in inventory_stock_lists:
#    print(_inventory.product_id , _inventory.quantity)


# warehouse_items = db.get_session().query(WarehouseItems).join(Warehouse).all()

# for item in warehouse_items:
#     print(item.quantity , item.warehouse_id , item.warehouse)


#person = db.get_session().query(Delivery).all()

#for p in person: 
#    print(p.name , p.delivery_logs)

#logs = db.get_session().query(DeliveryLogs).all()

#for log in logs:
#    print(log.boxes , log.delivery_person.name , log.notes)

orders = db.get_session().query(Order).all()

status = []

for order in orders:
    if order.status == "In-Transit":
            