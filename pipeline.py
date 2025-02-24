from typing import Dict, Any, Callable
from notification import send_alert
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.db import db
import config
import uuid

class AlertSystem:
    def __init__(self):
        self.alerts = []

    def send_log_to_db(self, message: str, data: Dict[str, Any], message_type: str, retailer_id: uuid.UUID):
        session = db.get_session()
        try:
            log_entry = BaylinkAlertLogs(
                retailer_id=  retailer_id,
                message=message,
                data=data,
                message_type=message_type,
            )
            session.add(log_entry)
            session.commit()
        except Exception as e:
            session.rollback()
            print(f"Failed to log alert to DB: {e}")
        finally:
            session.close()

    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any], retailer_id: uuid.UUID): 
        if event_name in config.ALERT_RULES: 
            condition: Callable[[Dict[str, Any]], bool] = config.ALERT_RULES[event_name]
        
            if condition(event_data):
                message = f"Alert: {event_name.replace('_', ' ').title()} - {event_data}"
                message_type = 'ALERT'
            else:
                message = f"No Alert: {event_name.replace('_', ' ').title()}"
                message_type = 'NO_ALERT'

            print("message", message)
            recipients = ['Aman Retailer']
            self.alerts.append({"message": message, "recipients": recipients})
            send_alert(message, recipients)

            self.send_log_to_db(message, event_data, message_type, retailer_id)

alert_system = AlertSystem()