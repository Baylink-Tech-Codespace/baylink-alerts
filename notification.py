import logging
import os

log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(filename=f"{log_dir}/alerts.log", level=logging.INFO, format="%(asctime)s - %(message)s")

def send_alert(message: str, recipients: list):
    """Sends alerts via logging or external service."""
    alert_msg = f"Alert sent to {', '.join(recipients)}: {message}"
    logging.info(alert_msg) 