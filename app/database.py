from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
from app import config
from app.config import settings

load_dotenv()

SQLALCHEMY_DATABASE_URI = settings.database_url

engine = create_engine(SQLALCHEMY_DATABASE_URI)

Sessionlocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = Sessionlocal()
    try:
        yield db
    finally:
        db.close()
