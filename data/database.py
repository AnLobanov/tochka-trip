from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base, Session
from data import models
from os import environ
import config

engine = create_engine(config.DB_SERVER)
base = declarative_base()
session = sessionmaker(engine)

def db_init():
    base.metadata.create_all(engine)

def db_depends():
    db = session()
    try:
        yield db
    finally:
        db.close()