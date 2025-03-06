from database.db import db
import select
import json
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


# CASE 29 
class RetailerVisitMonitor:
    def __init__(self):
        self.conn = None
        self.setup_retailer_visit_trigger()

    def setup_retailer_visit_trigger(self):
        """Set up the PostgreSQL trigger to detect low retailer visits."""
        try:
            raw_conn = db.engine.raw_connection()
            raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = raw_conn.cursor()

            cursor.execute("""
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

            cursor.execute("""
                DROP TRIGGER IF EXISTS retailer_visit_trigger ON "Retailer";
                CREATE TRIGGER retailer_visit_trigger
                AFTER UPDATE OF "lastVisited" ON "Retailer"
                FOR EACH ROW
                EXECUTE FUNCTION notify_low_retailer_visits();
            """)
            
            raw_conn.commit()

        except Exception as e:
            raise
        finally:
            cursor.close()
            raw_conn.close()

    def listen_for_low_visits(self):
        try:
            self.conn = db.engine.raw_connection()
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.conn.cursor()
            cursor.execute("LISTEN low_retailer_visits;")

            while True:
                if select.select([self.conn], [], [], 5) == ([], [], []):
                    continue
                
                self.conn.poll()
                
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    visit_data = json.loads(notify.payload)
                    
                    print(f"Alert: Retailer {visit_data['retailer_id']} visited only {visit_data['visit_count']} times this month!")

                    return visit_data

        except Exception as e:
            raise
        finally:
            if self.conn and not self.conn.closed:
                self.conn.close()

    def cleanup(self):
        if self.conn and not self.conn.closed:
            self.conn.close()


def process_low_retailer_visits(db_config):
    monitor = RetailerVisitMonitor()
    try:
        visit_alert = monitor.listen_for_low_visits()
        print(visit_alert)
        return visit_alert
    except KeyboardInterrupt:
        monitor.cleanup()
    except Exception as e:
        monitor.cleanup()
        raise
