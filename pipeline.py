from typing import Dict, Any
from notification import send_alert
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.db import db
from config import event_config
import json
        
from typing import List, Dict

class AlertSystem:
    def __init__(self):
        self.session = db.get_session()

    def group_alerts_by_recipient(self,alerts_data: List[List[Dict[str, str]]]) -> List[Dict[str, str]]:
        grouped_alerts = {}

        for sublist in alerts_data:
            for alert in sublist:
                recipient_key = 'recepient' if 'recepient' in alert else 'recipient'
                phone_number = alert[recipient_key]
                message = alert['message']
                person_name = alert['person_name']
                role = alert['role']

                if phone_number not in grouped_alerts:
                    grouped_alerts[phone_number] = {
                        "recipient": phone_number,
                        "messages": set(),
                        "person_name": person_name,
                        "role": role
                    }
                
                grouped_alerts[phone_number]["messages"].add(message)

        formatted_alerts = [
            {
                "recipient": data["recipient"],
                "messages": list(data["messages"]),
                "person_name": data["person_name"],
                "role": data["role"]
            }
            for data in grouped_alerts.values()
        ]

        return formatted_alerts

    def send_log_to_db(self, messages: List[str], data: Dict[str, Any]):
        try: 
            for message in messages:
                log_entry = BaylinkAlertLogs(
                    message=message, 
                    person_name=data['person_name'],
                    role=data['role'],
                    recepient = data['recepient']
                )
                self.session.add(log_entry)
                self.session.commit()
            
                send_alert(message, data['recepient'])
                print(f"Alert logged to DB")
        except Exception as e:
            self.session.rollback()
            print(f"Failed to log alert to DB: {e}")
        finally:
            self.session.close()
        
    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any]): 
        try: 
            alerts = []
            if event_name in event_config.keys():  
                conditions = event_config[event_name]
                
                if event_name == "recon_insert":
                    recon_id = json.loads(event_data)["_id"]
                    for condition in conditions: 
                        alerts.append(condition(recon_id))
                        
                elif event_name == "sudden_sales_drop":
                    event_data_json = json.loads(event_data)
                    
                    for condition in conditions: 
                        alerts.append(condition(event_data_json))

                elif event_name == "retailer_visit_too_short":
                    event_data_json = json.loads(event_data)
                    
                    for condition in conditions: 
                        alerts.append(condition(event_data_json))

                elif event_name == "order_insert":
                    event_data_json = json.loads(event_data)
                    
                    for condition in conditions: 
                        alerts.append(condition(event_data_json))

                elif event_name in ["daily_event_triggers" , "monthly_event_triggers"]:
                    for condition in conditions:   
                        alerts.append(condition(event_data))
                        
            alerts = self.group_alerts_by_recipient(alerts)
            
            with open("alerts.json", "w") as f:
                json.dump(alerts, f, indent=4)
           
            for alert in alerts:
            
              recipient = alert['recipient']
              messages = alert['messages']
              person_name = alert['person_name']
              role = alert['role']
              self.send_log_to_db(messages, {"recepient": recipient, "person_name": person_name, "role": role})
        
        except Exception as e:
            print(f"Alert Pipeline Failed: {e}")    
            
alert_system = AlertSystem() 
alert_system.alert_pipeline("",{})