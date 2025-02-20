import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from dotenv import load_dotenv

from database.base import Base 
load_dotenv()

class DB:
    def __init__(self):
        user = os.getenv("DB_USERNAME")
        password = os.getenv("DB_PASSWORD")
        host = os.getenv("DB_HOST")
        port = os.getenv("DB_PORT", "5432")
        database = os.getenv("DB_NAME")

        if not all([user, password, host, database]):
            raise ValueError("Database credentials are missing in the .env file.")

        self.db_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = scoped_session(sessionmaker(bind=self.engine, autoflush=False, autocommit=False))

    def get_session(self):
        return self.SessionLocal()

    def close_session(self):
        self.SessionLocal.remove()

db = DB()
Base.metadata.create_all(db.engine)
