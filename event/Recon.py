from database.db import db
from database.models.Recon import Recon
import select
import json
from sqlalchemy.exc import SQLAlchemyError
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

class ReconMonitor:
    def __init__(self):
        self.conn = None
        self.setup_database_trigger()

    def setup_database_trigger(self):
        """Set up the PostgreSQL trigger using the existing SQLAlchemy engine."""
        try:
            # Get a raw connection from the SQLAlchemy engine
            raw_conn = db.engine.raw_connection()
            raw_conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = raw_conn.cursor()
            
            # Create notification function
            cursor.execute("""
                CREATE OR REPLACE FUNCTION notify_recon_insert() RETURNS TRIGGER AS $$
                BEGIN
                    PERFORM pg_notify('recon_inserted', row_to_json(NEW)::text);
                    RETURN NEW;
                END;
                $$ LANGUAGE plpgsql;
            """)
            # logger.info("Notification function created successfully")
            
            # Create trigger
            cursor.execute("""
                DROP TRIGGER IF EXISTS recon_insert_trigger ON "Recon";
                CREATE TRIGGER recon_insert_trigger
                AFTER INSERT ON "Recon"
                FOR EACH ROW EXECUTE FUNCTION notify_recon_insert();
            """)
            # logger.info("Trigger created successfully")
            
            raw_conn.commit()
            
        except Exception as e:
            # logger.error(f"Error setting up database trigger: {str(e)}")
            raise
        finally:
            cursor.close()
            raw_conn.close()

    def process_recon(self, recon_data):
        """Process a recon record."""
        session = db.get_session()
        
        print("RECON DATA",recon_data)
        
        try:
            recon_id = recon_data['_id']
            # logger.info(f"Processing recon with ID: {recon_id}") 
            recon = session.query(Recon).filter(Recon._id == recon_id).first()
            
            print("RECON",recon) 
            
            # logger.debug(f"Retrieved recon: {recon}")
            
            if recon:
                quantity = sum(item.quantity for item in recon.ReconItems)
                image = recon.image[0] if recon.image else ""
                
                print(quantity , image , "RECON - QUANTITY / IMAGE ")
                
                event_data = {
                    "event_name": "is_retailer_shelf_image",
                    "event_data": {
                        "image_url": image,
                        "quantity": quantity,
                        "recon_id": str(recon._id),
                        "retailer_id": str(recon.retailer_id),
                        "recon_date": recon.recon_date.isoformat()
                    }
                }
                # logger.info(f"Processed new recon: {json.dumps(event_data)}")
                return event_data
            else:
                print("")
                # logger.warning(f"No recon found for ID: {recon_id}")
                
        except SQLAlchemyError as e:
            print("e")
            # logger.error(f"SQLAlchemy error processing recon {recon_id}: {str(e)}")
        except Exception as e:
            print("e")
            # logger.error(f"Unexpected error processing recon {recon_id}: {str(e)}")
        finally:
            db.close_session()

    def listen(self):
        try:
            self.conn = db.engine.raw_connection()
            self.conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = self.conn.cursor()
            cursor.execute("LISTEN recon_inserted;")
            # logger.info("Listening for 'recon_inserted' notifications...")
            
             
            while True:
                if select.select([self.conn], [], [], 5) == ([], [], []):
                    # logger.debug("No notifications received in the last 5 seconds")
                    continue
                
                self.conn.poll()
                # logger.debug(f"Number of notifications: {len(self.conn.notifies)}")
                
                while self.conn.notifies:
                    notify = self.conn.notifies.pop(0)
                    # logger.info(f"Received notification: {notify.payload}")
                    recon_data = json.loads(notify.payload)
                    recon_event = self.process_recon(recon_data)
                    if recon_event:
                        return recon_event
                    
        except Exception as e:
            # logger.error(f"Error in listen loop: {str(e)}")
            raise
        finally:
            if self.conn and not self.conn.closed:
                self.conn.close()
                # logger.info("Raw connection closed")

    def cleanup(self):
        """Clean up the connection."""
        if self.conn and not self.conn.closed:
            self.conn.close()
            # logger.info("Database connection closed")

def process_latest_recon(db_config):
    """Start the recon monitoring process."""
    monitor = ReconMonitor()
    try:
        recon_event = monitor.listen()
        return recon_event
    except KeyboardInterrupt:
        monitor.cleanup()
        # logger.info("Monitoring stopped by user")
    except Exception as e:
        monitor.cleanup()
        # logger.error(f"Monitoring failed: {str(e)}")
        raise 