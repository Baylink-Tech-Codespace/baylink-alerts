from database.db import db
from database.models.ASM import ASM 
from database.models.SuperZone import SuperZone
from database.models.Retailer import Retailer
from database.models.Recon import Recon
from database.models.Inventory import Inventory
from database.models.Inventory import InventoryStockList
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.models.Sales import Sales
from database.models.Warehouse import WarehouseItems, Warehouse
from database.models.DeliveryPerson import Delivery
from database.models.DeliveryLogs import DeliveryLogs
from database.models.Order import Order
from database.models.Product import Product , BatchCodes
from database.models.CreditNote import CreditNote , CreditNoteItems
from database.models.ASM import ASM
from database.models.Field_Exec import Field_Exec
from datetime import datetime
from database.models.BaylinkAlertLogs import BaylinkAlertLogs

from sqlalchemy.orm import configure_mappers
configure_mappers()


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


#products = db.get_session().query(Product).all()

#for product in products:
#    print(product.name , product.inventory_stock_list,product.batch_codes)


#inventories = db.get_session().query(Inventory).all()

#for inventory in inventories:
#    retailer = inventory.retailer
#    stock_lists = inventory.stock_lists
    
#    for stock in stock_lists:
#        product = stock.product
#        batch_codes = product.batch_codes
#        batch_codes.sort(key=lambda x: x.expiry_date)


#credit_notes = db.get_session().query(CreditNote).all()

#for credit_note in credit_notes:
#    print(credit_note.cn_name , credit_note.retailer.name)

#retailers = db.get_session().query(Retailer).all()

#for retailer in retailers:
#    print(retailer.recon , retailer.credit_notes , retailer.orders, retailer.sales)

#batchcodes = db.get_session().query(BatchCodes).all() 

#for batchcode in batchcodes:
#    print(batchcode.product_id , batchcode.product.name)

retailers = db.get_session().query(Retailer).all()

for retailer in retailers:
    if retailer and retailer.fe:
        print(retailer.fe.Name)