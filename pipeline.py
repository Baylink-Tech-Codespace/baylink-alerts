from typing import Dict, Any, Callable
from notification import send_alert
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.db import db
from config import event_config
import json
        
from typing import List, Dict
from typing import List, Dict


class AlertSystem:
    def __init__(self):
        self.session = db.get_session()

    def group_alerts_by_recipient(self, alerts_data: List[List[Dict[str, str]]]) -> List[Dict[str, str]]:
        """
        Groups alerts by recipient phone number, removes duplicate messages, and formats the output.

        Args:
            alerts_data: Nested list of alert dictionaries containing 'recepient'/'recipient' and 'message'

        Returns:
            List of dictionaries with 'recipient' and 'message' fields.
        """
        grouped_alerts = {}

        for sublist in alerts_data:
            for alert in sublist:
                recipient_key = 'recepient' if 'recepient' in alert else 'recipient'
                phone_number = alert[recipient_key]
                message = alert['message']

                if phone_number not in grouped_alerts:
                    grouped_alerts[phone_number] = set()
                
                grouped_alerts[phone_number].add(message)  # Using a set to avoid duplicates

        # Convert the grouped data into the required format
        formatted_alerts = [
            {"recipient": phone_number, "message": message}
            for phone_number, messages in grouped_alerts.items()
            for message in messages
        ]

        return formatted_alerts

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

            elif event_name in ["daily_event_triggers" , "monthly_event_triggers"]:
                for condition in conditions:  
                    alerts.append(condition(event_data))
                    
        alerts = self.group_alerts_by_recipient(alerts)
                    
        for alert in alerts:
            recepient = alert["recepient"]
            #person_name = alert["person_name"]
            #role = alert["role"] 
            message = alert["message"] 
            
            self.send_log_to_db(message, {
                "person_name": person_name,
                "role": role
            })
            
            send_alert(messages, "7007555103") # recepient
                
alert_system = AlertSystem() 