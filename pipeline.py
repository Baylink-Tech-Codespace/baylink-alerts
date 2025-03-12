from typing import Dict, Any, Callable
from notification import send_alert
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.db import db
from config import event_config
import json

class AlertSystem:
    def __init__(self):
        self.session = db.get_session()

    def send_log_to_db(self, message: str, data: Dict[str, Any]):
        try:
            log_entry = BaylinkAlertLogs(
                message=message, 
                person_name=data['person_name'],
                role=data['role']
            )
            self.session.add(log_entry)
            self.session.commit()
            print(f"Alert logged to DB")
        except Exception as e:
            self.session.rollback()
            print(f"Failed to log alert to DB: {e}")
        finally:
            self.session.close()
        
    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any]): 
        alerts = []
        if event_name in event_config.keys():  
            conditions = event_config[event_name]
            
            if event_name == "recon_inserted":
                recon_id = json.loads(event_data)["_id"]
                for condition in conditions: 
                    alerts.append(condition(recon_id))
                    
            elif event_name == "sudden_sales_drop":
                event_data_json = json.loads(event_data)
                
                for condition in conditions: 
                    alerts.append(condition(event_data_json))

            elif event_name == "daily_event_triggers":
                for condition in conditions: 
                    print("CONDITION",condition)
                    alerts.append(condition(event_data))
                    
        for alert in alerts:
            recepient = alert["recepient"]
            person_name = alert["person_name"]
            role = alert["role"] 
            messages = alert["messages"] 
            
            self.send_log_to_db(messages, {
                "person_name": person_name,
                "role": role
            })
            
            send_alert(messages, "7007555103") # recepient
                
alert_system = AlertSystem() 