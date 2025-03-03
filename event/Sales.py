from database.db import db
import select
import json
from sqlalchemy.exc import SQLAlchemyError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from config import check_sales_anomaly

class SalesDropMonitor:
    def __init__(self):
        self.conn = None
        self.setup_sales_drop_trigger()

    def setup_sales_drop_trigger(self):
        """Set up the PostgreSQL trigger to detect sudden sales drops."""
        try:
            raw_conn = db.engine.raw_connection()
            raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = raw_conn.cursor()

            # Create the notification function
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
            """)

            # Create the trigger
            cursor.execute("""
                DROP TRIGGER IF EXISTS sales_drop_trigger ON public.sales;
                CREATE TRIGGER sales_drop_trigger
                AFTER INSERT ON public.sales
                FOR EACH ROW
                EXECUTE FUNCTION notify_sudden_sales_drop();
            """)
            
            raw_conn.commit()
        
        except Exception as e:
            raise
        finally:
            cursor.close()
            raw_conn.close()

    def listen_for_sales_drop(self):
        try:
            self.conn = db.engine.raw_connection()
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.conn.cursor()
            cursor.execute("LISTEN sudden_sales_drop;")

            while True:
                if select.select([self.conn], [], [], 5) == ([], [], []):
                    continue
                
                self.conn.poll()
                
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    sales_drop_data = json.loads(notify.payload)
                     
                    session = db.get_session()
                    retailer_id = sales_drop_data['retailer_id']
                    product_id = sales_drop_data['product_id']
                    current_quantity = sales_drop_data['quantity']
                     
                    check_sales_anomaly(
                        session=session,
                        retailer_id=retailer_id,
                        product_id=product_id,
                        current_quantity=current_quantity,
                        threshold=0.5
                    )
                    
                    return sales_drop_data
                    
        except Exception as e:
            raise
        finally:
            if self.conn and not self.conn.closed:
                self.conn.close()

    def cleanup(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


def process_latest_sales_drop(db_config):
    monitor = SalesDropMonitor()
    try:
        sales_drop_event = monitor.listen_for_sales_drop()
        return sales_drop_event
    except KeyboardInterrupt:
        monitor.cleanup()
    except Exception as e:
        monitor.cleanup()
        raise
 