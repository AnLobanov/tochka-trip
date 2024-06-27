from sqlalchemy import Column, Integer, String, CheckConstraint, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import text, select
from datetime import datetime
from data import database
import uuid

class Profile(database.base):
    __tablename__ = 'profiles'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    name = Column(String(), nullable=False)
    auth = relationship("Auth")
    reservations = relationship("Reservation")

class Auth(database.base):
    __tablename__ = 'auth'

    id = Column(UUID(as_uuid=True), primary_key=True, unique=True, default=uuid.uuid4)
    verified = Column(Boolean(), default=False, nullable=False)
    email = Column(String(), CheckConstraint("email LIKE '%@%.%'"), nullable=False, unique=True)
    hashed = Column(String(), nullable=False)   
    sent = Column(DateTime(), nullable=False, default=datetime.now)
    role = Column(String(), nullable=False, default="user")
    user_id = Column(Integer(), ForeignKey("profiles.id"))
    user = relationship("Profile")

class Global(database.base):
    __tablename__ = 'globals'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False)
    autoverify = Column(Boolean(), default=True)

class Flight(database.base):
    __tablename__ = 'flights'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    number = Column(String(), nullable=False)
    arrival = Column(String(3), nullable=False)
    depatrure = Column(String(3), nullable=False)
    arrivalTime = Column(DateTime(), default=datetime.now)
    depatrureTime = Column(DateTime(), default=datetime.now)
    price = Column(Float(2), nullable=False)
    plane = Column(Integer, ForeignKey('planes.id'))

class Plane(database.base):
    __tablename__ = 'planes'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    company = Column(String(), nullable=False)
    number = Column(String(10), nullable=False)
    vendor = Column(String(), nullable=False)
    model = Column(String(), nullable=False)
    places = relationship('Place')

class Reservation_Place(database.base):
    __tablename__ = 'reservation_place'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)   
    reservation_id = Column(Integer(), ForeignKey('reservations.id'))
    place_id = Column(Integer(), ForeignKey('places.id'))

class Place(database.base):
    __tablename__ = 'places'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    row = Column(String(3), nullable=True)
    place = Column(String(3), nullable=False)
    plane = Column(Integer, ForeignKey('planes.id'))
    reservations = relationship("Reservation_Place", backref="place")

class Reservation(database.base):
    __tablename__ = 'reservations'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    status = Column(String(), nullable=False)
    profile = Column(Integer, ForeignKey('profiles.id'))
    flight = Column(Integer, ForeignKey('flights.id'))
    time = Column(DateTime(), nullable=False, default=datetime.now)
    price = Column(Float(2), nullable=False)
    return_url = Column(UUID(as_uuid=True), default=uuid.uuid4)
    places = relationship("Reservation_Place", backref="reservation")   

class Subscription(database.base):
    __tablename__ = 'subscriptions'

    id = Column(Integer(), primary_key=True, unique=True, nullable=False, autoincrement=True)
    profile = Column(Integer, ForeignKey('profiles.id'))
    flight = Column(Integer, ForeignKey('flights.id'))