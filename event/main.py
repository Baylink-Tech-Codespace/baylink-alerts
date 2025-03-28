import threading
import time
import schedule
import select
import psycopg2
from psycopg2 import pool
from pipeline import alert_system
import os
import dotenv

dotenv.load_dotenv()

class Monitor:
    def __init__(self):
        self.alert_system = alert_system
        self.running = False
        self.db_pool = None
        self.db_thread = None
        self.scheduler_thread = None
        
        try:
            self.db_pool = psycopg2.pool.ThreadedConnectionPool(
                minconn=1,
                maxconn=10,
                user=os.getenv("DB_USERNAME"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT", "5432"),
                database=os.getenv("DB_NAME"),
                connect_timeout=10
            )
        except Exception as e:
            print(f"Failed to initialize database pool: {e}")
            raise

    def setup_connection(self):
        if not self.db_pool:
            return None
        try:
            conn = self.db_pool.getconn()
            conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
            return conn
        except Exception as e:
            print(f"Error getting connection from pool: {e}")
            return None

    def setup_triggers(self, conn, cursor):
        try:
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_new_log() RETURNS TRIGGER AS $$
                DECLARE
                    new_log_data JSON;
                BEGIN
                    new_log_data := json_build_object(
                        'timestamp', NEW.timestamp,
                        'person_name', NEW.person_name,
                        'role', NEW.role,
                        'message', NEW.message
                    );

                    PERFORM pg_notify('new_log_channel', new_log_data::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_recon_insert() RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('recon_inserted', row_to_json(NEW)::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS recon_insert_trigger ON "Recon";
                CREATE TRIGGER recon_insert_trigger
                AFTER INSERT ON "Recon"
                FOR EACH ROW EXECUTE FUNCTION notify_recon_insert();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_sudden_sales_drop() RETURNS TRIGGER AS $$
                DECLARE
                    prev_quantity INTEGER;
                BEGIN
                    SELECT quantity
                    INTO prev_quantity
                    FROM public.sales
                    WHERE retailer_id = NEW.retailer_id AND product_id = NEW.product_id
                    ORDER BY date DESC
                    LIMIT 1 OFFSET 1;

                    IF prev_quantity IS NOT NULL AND NEW.quantity < 0.8 * prev_quantity THEN
                        PERFORM pg_notify('sudden_sales_drop', json_build_object(
                            'retailer_id', NEW.retailer_id,
                            'product_id', NEW.product_id,
                            'date', NEW.date,
                            'quantity', NEW.quantity,
                            'prev_quantity', prev_quantity,
                            'alert_status', 'ALERT: Sudden Drop in Sales'
                        )::text);
                    END IF;
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS sales_drop_trigger ON public.sales;
                CREATE TRIGGER sales_drop_trigger
                AFTER INSERT ON public.sales
                FOR EACH ROW EXECUTE FUNCTION notify_sudden_sales_drop();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION retailer_visit_too_short() RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('retailer_visit_too_short', row_to_json(NEW)::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;

                DROP TRIGGER IF EXISTS retailer_visit_too_short_trigger ON "RetailerVisitedLog";

                CREATE TRIGGER retailer_visit_too_short_trigger
                AFTER UPDATE ON "RetailerVisitedLog"
                FOR EACH ROW
                WHEN (NEW.visit_start IS NOT NULL AND NEW.visit_end IS NOT NULL)
                EXECUTE FUNCTION notify_retailer_visit_too_short();
            """)

            cursor.execute("""
                CREATE OR REPLACE FUNCTION order_insert() RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('order_inserted', row_to_json(NEW)::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
                
                DROP TRIGGER IF EXISTS order_insert_trigger ON "Order";
                CREATE TRIGGER order_insert_trigger
                AFTER INSERT ON "Order"
                FOR EACH ROW EXECUTE FUNCTION notify_order_insert();
            """)

            conn.commit()
        except Exception as e:
            print(f"Error setting up triggers: {e}")
            conn.rollback()

    def daily_event_triggers(self):
        try:
            event_name = "daily_event_triggers"
            event_data = ""
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Executing daily triggers at {current_time}")
            self.alert_system.alert_pipeline(event_name, event_data)
        except Exception as e:
            print(f"Error in daily triggers: {e}")

    def monthly_event_triggers(self):
        try:
            event_name = "monthly_event_triggers"
            event_data = ""
            current_time = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"Executing monthly triggers at {current_time}")
            self.alert_system.alert_pipeline(event_name, event_data)
        except Exception as e:
            print(f"Error in monthly triggers: {e}")

    def listen_database(self):
        conn = self.setup_connection()
        if not conn:
            return

        try:
            cursor = conn.cursor()
            self.setup_triggers(conn, cursor)
            cursor.execute("LISTEN recon_insert_trigger; LISTEN sales_drop_trigger; LISTEN retailer_visit_too_short_trigger; LISTEN order_insert_trigger")
            print("Listening for database notifications...")

            while self.running:
                if select.select([conn], [], [], 5) == ([], [], []):
                    continue
                
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    print(f"Received notification on channel '{notify.channel}': {notify.payload}")
                    self.alert_system.alert_pipeline(notify.channel, notify.payload)
                
                time.sleep(0.1)

        except Exception as e:
            print(f"Error in database listener: {e}")
        finally:
            if 'cursor' in locals():
                cursor.close()
            if conn:
                self.db_pool.putconn(conn)

    def run_scheduler(self):
        if not self.running:
            return
            
        # Clear any existing jobs to prevent duplicates
        schedule.clear()
        
        # Schedule jobs
        schedule.every().day.at("14:46").do(self.daily_event_triggers)
        schedule.every(30).days.at("11:18").do(self.monthly_event_triggers)
        
        print("Scheduler started for daily/monthly triggers...")
        print(f"Next daily run scheduled for: {schedule.next_run()}")

        while self.running:
            try:
                # Print current time and next scheduled run for debugging
                # current_time = time.strftime('%Y-%m-%d %H:%M:%S')
                # next_run = schedule.next_run()
                
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                print(f"Error in scheduler: {e}")
                time.sleep(5)

    def listen_triggers(self):
        if self.running:
            print("Monitor already running")
            return

        self.running = True

        self.db_thread = threading.Thread(target=self.listen_database, name="DBListener")
        self.db_thread.daemon = True
        self.db_thread.start()

        self.scheduler_thread = threading.Thread(target=self.run_scheduler, name="Scheduler")
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

        try:
            while self.running and (self.db_thread.is_alive() or self.scheduler_thread.is_alive()):
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        """Clean shutdown of monitor"""
        self.running = False
        schedule.clear()  # Clear scheduled jobs
        if self.db_pool:
            self.db_pool.closeall()
        print("Monitor stopped")

if __name__ == "__main__":
    monitor = Monitor()
    monitor.listen_triggers()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        monitor.stop()