
import select
from database.db import db
from config import event_config
from pipeline import alert_system
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class Monitor:
    def __init__(self):
        self.raw_connection = None
        self.cursor = None
        self.alert_system = alert_system
        
    def setup_connection(self):
        self.raw_connection = db.engine.raw_connection()
        self.raw_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        self.cursor = self.raw_connection.cursor()
        
    def recon_insert_listener(self):
        try:
            self.cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_recon_insert() RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('recon_inserted', row_to_json(NEW)::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            
            self.cursor.execute("""
                DROP TRIGGER IF EXISTS recon_insert_trigger ON "Recon";
                CREATE TRIGGER recon_insert_trigger
                AFTER INSERT ON "Recon"
                FOR EACH ROW EXECUTE FUNCTION notify_recon_insert();
            """)
           
            self.raw_connection.commit()

        except Exception as e:
            print(e)
            return 
            
    def sales_insert_listener(self):
        try:
            self.cursor.execute("""
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
            """)
            
            self.cursor.execute("""
                DROP TRIGGER IF EXISTS sales_drop_trigger ON public.sales;
                CREATE TRIGGER sales_drop_trigger
                AFTER INSERT ON public.sales
                FOR EACH ROW
                EXECUTE FUNCTION notify_sudden_sales_drop();
            """)
            
            self.raw_connection.commit()
            
        except Exception as e:
            print(e)
            return
            
    def retailer_visit_listener(self):
        try:
            self.cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_low_retailer_visits() RETURNS TRIGGER AS $$
                DECLARE
                    visit_count INTEGER;
                BEGIN
                    SELECT COUNT(*)
                    INTO visit_count
                    FROM "Retailer"
                    WHERE _id = NEW._id
                    AND EXTRACT(YEAR FROM "lastVisited") = EXTRACT(YEAR FROM NOW())
                    AND EXTRACT(MONTH FROM "lastVisited") = EXTRACT(MONTH FROM NOW());

                    IF visit_count < 4 THEN
                        PERFORM pg_notify('low_retailer_visits', json_build_object(
                            'retailer_id', NEW._id,
                            'visit_count', visit_count,
                            'alert_status', 'ALERT: Less than 4 visits this month'
                        )::text);
                    END IF;

                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)

            self.cursor.execute("""
                DROP TRIGGER IF EXISTS retailer_visit_trigger ON "Retailer";
                CREATE TRIGGER retailer_visit_trigger
                AFTER UPDATE OF "lastVisited" ON "Retailer"
                FOR EACH ROW
                EXECUTE FUNCTION notify_low_retailer_visits();
            """)
            
            self.raw_connection.commit()
            
        except Exception as e:
            print(e)
            return
            
    def start_listening(self):
        try: 
            self.cursor.execute("LISTEN recon_inserted;")
            self.cursor.execute("LISTEN sudden_sales_drop;")
            self.cursor.execute("LISTEN low_retailer_visits;")
            
            print("Listening for notifications...")
             
            while True: 
                if select.select([self.raw_connection], [], [], 10) == ([], [], []):
                    continue
                
                self.raw_connection.poll()
                while self.raw_connection.notifies:
                    notify = self.raw_connection.notifies.pop(0)
                    print(f"Received notification on channel '{notify.channel}': {notify.payload}")
                    self.alert_system.alert_pipeline(notify.channel, notify.payload)
        
        except Exception as e:
            print(f"Error while listening for triggers: {e}")
            
    def listen_triggers(self):
        try:
            self.setup_connection()
            self.recon_insert_listener()
            self.sales_insert_listener()
            self.retailer_visit_listener()
             
            self.start_listening()
            
        except Exception as e:
            print(e)
        finally:
            if self.cursor:
                self.cursor.close()
            if self.raw_connection:
                self.raw_connection.close()
                
        
monitor = Monitor() 

