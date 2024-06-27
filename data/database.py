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
    db = Session(bind=engine.connect())
    db.add(models.Global())
    db.commit()
    db.add(models.Plane(vendor="Airbus", model="A320", company="S7", number="VQ-BRD"))
    db.add(models.Plane(vendor="Boeing", model="737", company="Aeroflot", number="VP-BBR"))
    db.commit()
    db.add(models.Place(plane=1, row=1, place=1))
    db.add(models.Place(plane=1, row=1, place=2))
    db.add(models.Place(plane=1, row=2, place=1))
    db.add(models.Place(plane=1, row=2, place=2))
    db.add(models.Place(plane=2, row=1, place=1))
    db.add(models.Place(plane=2, row=1, place=2))
    db.add(models.Place(plane=2, row=1, place=3))
    db.add(models.Place(plane=2, row=1, place=3))
    db.commit()
    db.add(models.Flight(number="SU123", arrival="SVO", depatrure="LED", price=1000.99, plane=1, arrivalTime="2021-09-01 12:00:00", depatrureTime="2021-09-01 10:00:00"))
    db.commit()

def db_depends():
    db = session()
    try:
        yield db
    finally:
        db.close()