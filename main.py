import schedule  
import time
import threading
from flask import Flask, render_template
from flask_socketio import SocketIO
from events import get_test_event
from pipeline import alert_system

LOG_FILE = "logs/alerts.log"

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def process_alerts():
    test_event = get_test_event()
    alert_system.alert_pipeline(
        event_name=test_event["event_name"],
        event_data=test_event["event_data"]
    )

schedule.every(1).seconds.do(process_alerts)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
 
def tail_log():
    with open(LOG_FILE, "r") as file:
        while True:
            line = file.readline()
            if line:
                socketio.emit("new_log", {"message": line.strip()})
            else:
                time.sleep(1)

@app.route("/")
def index():
    return render_template("index.html")

if __name__ == "__main__":
    print("🚀 Alert System & Dashboard Running...")

    threading.Thread(target=run_scheduler, daemon=True).start()
    threading.Thread(target=tail_log, daemon=True).start()
    print(f"Open URL : http://localhost:{3000} to access the dashboard.")
    socketio.run(app, host="0.0.0.0", port=3000, debug=True)
    
