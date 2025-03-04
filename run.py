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

#retailers = db.get_session().query(Retailer).all() 
#recons = db.get_session().query(Recon).all()

#logs = db.get_session().query(BaylinkAlertLogs).all()

#for log in logs:
 #   print(log.data,log.message , log.message_type)


# inventories = db.get_session().query(Inventory).all()
#inventory_stock_lists = db.get_session().query(InventoryStockList).all()

#for _inventory in inventory_stock_lists:
#    print(_inventory.product_id , _inventory.quantity)


warehouse_items = db.get_session().query(WarehouseItems).join(Warehouse).all()

for item in warehouse_items:
    print(item.quantity , item.warehouse_id , item.warehouse)