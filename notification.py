import logging
import os
import requests
from typing import Union, List

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f"{log_dir}/alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

# Update to use WA Microservice URL, update once it is deployed.
WA_MICROSERVICE_URL = "http://localhost:3005/api/send-alert"

def send_alert(message: str, recipient: Union[str, List[str]]) -> None:
    """
    Sends alerts via WhatsApp Microservice.
    
    Args:
        message (str): Alert message to send
        recipient (str or list): Phone number(s) to send alert to
    """
    # Convert single recipient to list for consistent handling
    recipients = [recipient] if isinstance(recipient, str) else recipient
    
    for phone in recipients:
        alert_msg = f"Alert for {phone}: {message}"
        print('Sending alert:', alert_msg)
        
        try:
            response = requests.post(
                WA_MICROSERVICE_URL,
                json={
                    "phoneNumber": phone,
                    "message": message
                },
                timeout=10
            )
            
            response.raise_for_status()
            
            if response.json().get('success'):
                logging.info(f"Alert sent successfully to {phone}: {message}")
            else:
                logging.error(f"Failed to send alert to {phone}: {response.json().get('error')}")
                
        except requests.exceptions.RequestException as e:
            logging.error(f"Error sending alert to {phone}: {str(e)}")
            print(f"Error sending alert: {str(e)}")