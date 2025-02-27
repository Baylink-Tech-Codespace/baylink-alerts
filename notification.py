import logging
import os
import requests

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f"{log_dir}/alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

WHATSAPP_API_URL = "https://api.whatsapp.com/send"

def send_alert(message: str, recipient: list):
    """Sends alerts via logging or external service."""
    alert_msg = f"Alert sent to {recipient}: {message}"
    print('alert msg',alert_msg)
    
    response = requests.post(WHATSAPP_API_URL, params={"phone": recipient, "text": message})
    
    if response.status_code != 200:
        logging.error(f"Failed to send alert to {recipient}: {response.text}")
        
    else:
        logging.info(f"Alert sent to {recipient}: {message}")  