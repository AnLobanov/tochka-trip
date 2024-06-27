import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy_utils import database_exists, drop_database, create_database
from data import database, models
from main import app
from config import DB_SERVER

@pytest.fixture(scope="session")
def db_engine():
    engine = create_engine(DB_SERVER + "test")
    if not database_exists(DB_SERVER + "test"):
        create_database(DB_SERVER + "test")
    database.base.metadata.create_all(bind=engine)
    yield engine
    drop_database(DB_SERVER + "test")

@pytest.fixture(scope="function")
def db(db_engine):
    connection = db_engine.connect()
    db = Session(bind=connection)
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
    yield db
    db.rollback()
    connection.close()
 
@pytest.fixture(scope="function")
def client(db):
    app.dependency_overrides[database.db_depends] = lambda: db
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="module")
def global_data():
    return {'access_token': '',
            'refresh_token': '',
            'id': ''}