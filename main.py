import schedule  
import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from pipeline import alert_system
from event.Recon import process_latest_recon
import os 
import _asyncio
import dotenv
dotenv.load_dotenv()

LOG_FILE = "logs/alerts.log"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

db_config = { 
    "user" : os.getenv("DB_USERNAME"),
    "password" : os.getenv("DB_PASSWORD"),
    "host" : os.getenv("DB_HOST"),
    "port" : os.getenv("DB_PORT", "5432"),
    "database" : os.getenv("DB_NAME"), 
}

async def process_alerts():
    recon_event = process_latest_recon(db_config)
     
    await alert_system.alert_pipeline(
        event_name=recon_event["event_name"],
        event_data=recon_event["event_data"], 
    )

schedule.every(1).seconds.do(process_alerts)

async def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
 
async def tail_log():
    print(f"Attempting to read from log file: {LOG_FILE}")  
    if not os.path.exists(LOG_FILE):
        print(f"Log file {LOG_FILE} does not exist - creating it")
        open(LOG_FILE, 'a').close()
    
    with open(LOG_FILE, "r") as file:
        file.seek(0, os.SEEK_END)  
        while True:
            line = file.readline()
            if line:
                print(f"Emitting log line: {line.strip()}")  
                await socketio.emit("new_log", {"message": line.strip()})
            else:
                time.sleep(0.1)

@app.route("/")
async def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("🚀 Alert System & Dashboard Running...")

    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=tail_log, daemon=True).start()
    print(f"Open URL : http://localhost:{3000} to access the dashboard.")
    socketio.run(app, host="0.0.0.0", port=3000, debug=True)
    
