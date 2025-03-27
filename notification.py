import logging
import os 
import requests
from constants import get_wa_alert_template

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f"{log_dir}/alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

WA_MICROSERVICE_URL = "https://whatsapp.baylink.in/send-message"

def formatted_phone(number):
    if not number : return None
    return "91" + number

def send_alert(message: str, recipient: str) -> None:
    template = get_wa_alert_template(recipient, message)
    
    try:
        response = requests.post(
            WA_MICROSERVICE_URL,
            json=template,
            timeout=10
        )
        
        response.raise_for_status()
        
        if response.json().get('success'):
            logging.info(f"Alert sent successfully to {recipient}: {message}")
        else:
            logging.error(f"Failed to send alert to {recipient}: {response.json().get('error')}")
            
    except requests.exceptions.RequestException as e:
        logging.error(f"Error sending alert to {recipient}: {str(e)}")
        print(f"Error sending alert: {str(e)}")
           

