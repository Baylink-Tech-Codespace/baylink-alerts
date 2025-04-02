from typing import Dict, Any, List
from notification import send_alert
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from database.db import db
from config import event_config
import json
import os
from pdf.main import PDFGenerator

class AlertSystem:
    def __init__(self):
        self.session = db.get_session()
        self.scheduled_alert_file_name = "grouped_scheduled_alerts.json"
        self.pdf_generator = PDFGenerator()

    def group_alerts_by_recipient_event_(self,alerts_data):
        grouped_alerts = {}
        
        print("Grouping alerts by recipient...")
        print(alerts_data)
        
        for alert in alerts_data:
            recipient = alert["recipient"]
            if recipient not in grouped_alerts:
                grouped_alerts[recipient] = {
                    "recipient": recipient,
                    "person_name": alert["person_name"],
                    "role": alert["role"],
                    "messages": set()
                }
            
            grouped_alerts[recipient]["messages"].update(filter(None, alert["messages"]))  # Removes empty strings and ensures uniqueness
        
        return [{
            "recipient": data["recipient"],
            "messages": list(data["messages"]),
            "person_name": data["person_name"],
            "role": data["role"]
        } for data in grouped_alerts.values()]
        
    def group_alerts_by_recipient_scheduled_(self, alerts_data):
        grouped_alerts = {}

        print("Grouping alerts by recipient...")
        print(alerts_data)
        
        for alert_list in alerts_data:  # Iterate over the outer list
            for alert in alert_list:  # Iterate over each sublist
                recipient = alert["recipient"]
                if recipient not in grouped_alerts:
                    grouped_alerts[recipient] = {
                        "recipient": recipient,
                        "person_name": alert["person_name"],
                        "role": alert["role"],
                        "messages": set()
                    }
                
                grouped_alerts[recipient]["messages"].add(alert["message"])  # Ensure uniqueness
        
        return [{
            "recipient": data["recipient"],
            "messages": list(data["messages"]),
            "person_name": data["person_name"],
            "role": data["role"]
        } for data in grouped_alerts.values()]
        
    def send_log_to_db(self, messages: List[str], data: Dict[str, Any]):
        try:
            print("Logging alert to DB...")
             
            for message in messages:
                log_entry = BaylinkAlertLogs(
                    message=message,
                    person_name=data['person_name'],
                    role=data['role'],
                    recipient=data['recipient']
                )
                self.session.add(log_entry)
            self.session.commit()
            print("Alert logged to DB")
        except Exception as e:
            self.session.rollback()
            print(f"Failed to log alert to DB: {e}")
        finally:
            self.session.close()

    def send_notification(self, messages: List[str], data: Dict[str, Any]):
        for message in messages:
            send_alert(message, "7007555103" ) # data['recipient'])
            print(f"Alert sent to {data['recipient']}")

    def process_event_alerts(self, event_name: str, event_data: Dict[str, Any]):
        event_based_alerts = []
        if event_name in event_config:
            conditions = event_config[event_name]
            parsed_event_data = json.loads(event_data)

            for condition in conditions:
                result = condition(parsed_event_data)
                if result is not None and len(result) > 0:
                    event_based_alerts.append(condition(parsed_event_data))
        
        if event_based_alerts is not None and len(event_based_alerts) > 0:
            grouped_event_alerts = self.group_alerts_by_recipient_event_(event_based_alerts)
            
            with open("grouped_event_alerts.json", "w") as f:
                json.dump(grouped_event_alerts, f, indent=4)
            
            for alert in grouped_event_alerts:
                self.send_log_to_db(alert['messages'], alert)
                self.send_notification(alert['messages'], alert)

    def process_scheduled_alerts(self, event_name: str, event_data: Dict[str, Any]):
        alerts = []
        conditions = event_config.get(event_name, [])
        for condition in conditions:
            result = condition(event_data)
            
            if result is not None and len(result) > 0:
                alerts.append(result)
        
        grouped_alerts = self.group_alerts_by_recipient_scheduled_(alerts)
        with open(self.scheduled_alert_file_name, "w") as f:
            json.dump(grouped_alerts, f, indent=4)
        
        print("Scheduled alerts saved to ",self.scheduled_alert_file_name)
        
        return grouped_alerts

    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any]):
        try:
            print("Alert Pipeline Started...")
            
            grouped_alerts = []
            
            if event_name in ["daily_event_triggers", "monthly_event_triggers"]:
                grouped_alerts = self.process_scheduled_alerts(event_name, event_data)
            else:
                self.process_event_alerts(event_name, event_data)
                
            if event_name in ["daily_event_triggers", "monthly_event_triggers"]:    
                if os.path.exists(self.scheduled_alert_file_name) and os.path.getsize(self.scheduled_alert_file_name) > 0:
                    
                    for alert in grouped_alerts:
                        self.send_log_to_db(alert['messages'], alert)
                    
                    print("Generating PDFs for scheduled alerts...")
                    self.pdf_generator.generate_and_send_pdfs()
                    
        except Exception as e:
            print(f"Alert Pipeline Failed: {e}")
            
            
alert_system = AlertSystem()

# changed the number on notification'