import random

def get_test_event() -> dict:
    event_types = ["pending_payment", "low_inventory", "sales_drop", "stock_near_expiry"]
    
    event_name = random.choice(event_types)  

    event_data = {
        "pending_payment": {
            "pending_days": random.randint(30, 90),  
            "pending_bills": random.randint(1, 5)
        },
        "low_inventory": {
            "current_stock": random.randint(0, 100),
            "required_stock": random.randint(100, 300)
        },
        "sales_drop": {
            "current_sales": random.randint(50, 500),
            "historical_avg_sales": random.randint(200, 800)
        },
        "stock_near_expiry": {
            "days_to_expiry": random.randint(5, 40)
        }
    }

    return {
        "event_name": event_name,
        "event_data": event_data[event_name]
    }
