 
from typing import Dict, Any, Callable
from notification import send_alert
import config

class AlertSystem:
    def __init__(self):
        self.alerts = []  

    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any]): 

        if event_name in config.ALERT_RULES: 
            condition: Callable[[Dict[str, Any]], bool] = config.ALERT_RULES[event_name]
        
            if condition(event_data):
                message = f"Alert: {event_name.replace('_', ' ').title()} - {event_data}"
                print(message)
                recipients = ['Aman Retailer']
                self.alerts.append({"message": message, "recipients": recipients})
                send_alert(message, recipients)
        else:
            print("Invalid event name:", event_name)
 
alert_system = AlertSystem()
