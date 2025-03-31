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
        self.alert_file_name = "alerts.json"
        self.pdf_generator = PDFGenerator()

    def group_alerts_by_recipient(self, alerts_data: List[List[Dict[str, str]]]) -> List[Dict[str, Any]]:
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

        return [
            {
                "recipient": data["recipient"],
                "messages": list(data["messages"]),
                "person_name": data["person_name"],
                "role": data["role"]
            }
            for data in grouped_alerts.values()
        ]

    def send_log_to_db(self, messages: List[str], data: Dict[str, Any]):
        try:
            for message in messages:
                log_entry = BaylinkAlertLogs(
                    message=message,
                    person_name=data['person_name'],
                    role=data['role'],
                    recepient=data['recepient']
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
            send_alert(message, "7007555103" ) # data['recepient'])
            print(f"Alert sent to {data['recepient']}")

    def process_event_alerts(self, event_name: str, event_data: Dict[str, Any]):
        event_based_alerts = []
        if event_name in event_config:
            conditions = event_config[event_name]
            parsed_event_data = json.loads(event_data)

            for condition in conditions:
                event_based_alerts.append(condition(parsed_event_data))

        grouped_event_alerts = self.group_alerts_by_recipient(event_based_alerts)
        
        for alert in grouped_event_alerts:
            self.send_log_to_db(alert['messages'], alert)
            self.send_notification(alert['messages'], alert)

    def process_scheduled_alerts(self, event_name: str, event_data: Dict[str, Any]):
        alerts = []
        if event_name in ["daily_event_triggers", "monthly_event_triggers"]:
            conditions = event_config.get(event_name, [])
            for condition in conditions:
                alerts.append(condition(event_data))
        
        grouped_alerts = self.group_alerts_by_recipient(alerts)
        with open(self.alert_file_name, "w") as f:
            json.dump(grouped_alerts, f, indent=4)
        
        print("Scheduled alerts saved to alerts.json")

    def alert_pipeline(self, event_name: str, event_data: Dict[str, Any]):
        try:
            if event_name in ["daily_event_triggers", "monthly_event_triggers"]:
                self.process_scheduled_alerts(event_name, event_data)
            else:
                self.process_event_alerts(event_name, event_data)
            
            if os.path.exists(self.alert_file_name) and os.path.getsize(self.alert_file_name) > 0:
                print("Generating PDFs for scheduled alerts...")
                self.pdf_generator.generate_and_send_pdfs()
        except Exception as e:
            print(f"Alert Pipeline Failed: {e}")
            
            
alert_system = AlertSystem()




# changed the number on notification'