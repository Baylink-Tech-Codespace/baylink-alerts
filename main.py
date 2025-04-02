import schedule
import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO 
from event.main import Monitor
from database.models.BaylinkAlertLogs import BaylinkAlertLogs
from flask import jsonify
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import os 
import dotenv 
from datetime import datetime
from database.db import db

dotenv.load_dotenv()

LOG_FILE = "logs/alerts.log"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def process_alerts():
    print("Processing alerts...")
    monitor = Monitor() 
    monitor.listen_triggers() 
    

# schedule.every(90).seconds.do(process_alerts)

def run_scheduler():
    
    process_alerts()
    
    while True:
        schedule.run_pending()
        time.sleep(1)

@app.route('/fetch_logs', methods=['GET'])
def fetch_logs():
    """Fetch all logs from DB when client connects."""
    session = db.get_session()
    logs = session.query(BaylinkAlertLogs).order_by(BaylinkAlertLogs.timestamp.desc()).all()
    session.close()

    log_data = [
        {
            "timestamp": log.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "retailer": log.person_name,   
            "alert_type": log.role, 
            "details": log.message,
        }
        for log in logs
    ]

    return jsonify(log_data)

def notify_clients(new_log):
    formatted_timestamp = datetime.fromisoformat(new_log["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    socketio.emit("new_log", {
        "timestamp":formatted_timestamp,
        "retailer": new_log["person_name"],
        "alert_type": new_log["role"],
        "details": new_log["message"],
    }) 
    
def listen_to_db():
    """Listen for new log inserts in PostgreSQL and notify clients."""
    conn = psycopg2.connect(
        user=os.getenv("DB_USERNAME"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME"),
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute("LISTEN new_log_channel;")

    while True:
        conn.poll()
        while conn.notifies:
            notify = conn.notifies.pop(0)
            
            print(notify.payload , notify.channel)
            new_log = eval(notify.payload)  
            notify_clients(new_log)   

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("🚀 Alert System & Dashboard Running...")
    
    run_scheduler()

    # threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=listen_to_db, daemon=True).start()

    print(f"Open URL : http://localhost:{4000} to access the dashboard.")
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)
