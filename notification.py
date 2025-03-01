import logging
import os
import requests
from typing import Union, List

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f"{log_dir}/alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

WA_MICROSERVICE_URL = "http://localhost:8080/api/send-alert"

def send_alert(message: str, recipient: str) -> None:
    """
    Sends alerts via WhatsApp Microservice.
    
    Args:
        message (str): Alert message to send
        recipient (str or list): Phone number(s) to send alert to
    """
    
    alert_msg = f"Alert for {recipient}: {message}"
    
    try:
        response = requests.post(
            WA_MICROSERVICE_URL,
            json={
                "phoneNumber": recipient,
                "message": message
            },
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
         