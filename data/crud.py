from sqlalchemy.orm import Session, load_only
from data import models, schemas
from auth import hash
from datetime import datetime
from config import BASE_URL
import uuid

def init_mock(db: Session):
    db.add(models.Global())
    db.commit()
    db.add(models.Plane(vendor="Airbus", model="A320", company="S7", number="VQ-BRD"))
    db.add(models.Plane(vendor="Boeing", model="737", company="Aeroflot", number="VP-BBR"))
    db.commit()
    db.add(models.Place(plane=1, row=1, place=1))
    db.add(models.Place(plane=1, row=1, place=2))
    db.add(models.Place(plane=1, row=2, place=1))
    db.add(models.Place(plane=1, row=2, place=2))
    db.commit()
    db.add(models.Flight(number="SU123", arrival="SVO", depatrure="LED", price=1000.99, plane=1, arrivalTime="2021-09-01 12:00:00", depatrureTime="2021-09-01 10:00:00"))
    db.add(models.Flight(number="SU321", arrival="LED", depatrure="SVO", price=1000.99, plane=2, arrivalTime="2021-09-02 10:00:00", depatrureTime="2021-09-02 12:00:00"))
    db.commit()


class Auth:
    def user_exists(db: Session, email: str) -> bool:
        return bool(db.query(models.Auth).filter(models.Auth.email == email).first())

    def get_id(db: Session, email: str) -> str:
        return db.query(models.Auth).filter(models.Auth.email == email).first().id

    def get_profile_id(db: Session, email: str) -> int:
        return db.query(models.Auth).filter(models.Auth.email == email).first().user_id

    def get_role(db: Session, email: str) -> str:
        return db.query(models.Auth).filter(models.Auth.email == email).first().role

    def create_profile(db: Session, profile: schemas.ProfileCreate) -> models.Profile:
        db_profile = models.Profile(name=profile.name)
        db.add(db_profile)
        db.commit()
        db.refresh(db_profile)
        return db_profile

    def create_auth(db: Session, auth: schemas.Auth, profile_id: int) -> models.Auth:
        db_auth = models.Auth(email=auth.email, hashed=hash.hash(auth.password), user_id=profile_id, role=auth.role, sent=datetime.today())
        db.add(db_auth)
        db.commit()
        db.refresh(db_auth)
        return db_auth

    def get_auth(db: Session, id: str) -> models.Auth:
        return db.query(models.Auth).filter(models.Auth.id == uuid.UUID(id)).first()

    def verified(db: Session, id: str) -> bool:
        return db.query(models.Auth).filter(models.Auth.id == uuid.UUID(id)).first().verified

    def verified_email(db: Session, email: str) -> bool:
        return db.query(models.Auth).filter(models.Auth.email == email).first().verified

    def verify(db: Session, id: str):
        db_auth = db.query(models.Auth).get(uuid.UUID(id))
        db_auth.verified = True
        db.commit()

    def get_hashed(db: Session, email: str) -> str:
        return db.query(models.Auth).filter(models.Auth.email == email).first().hashed

    def get_sent(db: Session, email: str):
        return db.query(models.Auth).filter(models.Auth.email == email).first().sent

    def change_sent(db: Session, email: str, sent: datetime):
        id = db.query(models.Auth).filter(models.Auth.email == email).first().id
        db_auth = db.query(models.Auth).get(id)
        db_auth.sent = sent
        db.commit()

    def create_auth_id(db: Session, email: str):
        id = db.query(models.Auth).filter(models.Auth.email == email).first().id
        db_auth = db.query(models.Auth).get(id)
        new_id = uuid.uuid4()
        db_auth.id = new_id
        db.commit()
        return new_id

    def change_password(db: Session, id: str, password: str):
        db_auth = db.query(models.Auth).get(uuid.UUID(id))
        db_auth.hashed = hash.hash(password)
        db.commit()

    def get_email(db: Session, id: str):
        return db.query(models.Auth).get(uuid.UUID(id)).email
    
    def get_email_by_profile(db: Session, id: int):
        return db.query(models.Auth).filter(models.Auth.user_id == id).first().email
    
class Booking:
    def get_flights(db: Session) -> list:
        flights = db.query(models.Flight).all()
        result = [flight.__dict__ for flight in flights]
        for flight in result:
            places = db.query(models.Place).options(load_only(models.Place.id, models.Place.row, models.Place.place)).filter(models.Place.plane == flight["plane"]).all()
            reservations = db.query(models.Reservation).filter(models.Reservation.flight == flight["id"], models.Reservation.status != "canceled").all()
            occupied = []
            for reservation in reservations:
                for place in reservation.places:
                    occupied.append(place.place_id)
            freeplaces = []
            for place in places:
                if place.id not in occupied:
                    freeplaces.append(place)
            flight["places"] = freeplaces
            flight["plane"] = db.query(models.Plane).filter(models.Place.id == flight["plane"]).first().__dict__
        return result
    
    def get_free_places(db: Session, id: int) -> list:
        places = db.query(models.Place).options(load_only(models.Place.id, models.Place.row, models.Place.place)).filter(models.Place.plane == id).all()
        reservations = db.query(models.Reservation).filter(models.Reservation.flight == id, models.Reservation.status != "canceled").all()
        occupied = []
        for reservation in reservations:
            for place in reservation.places:
                occupied.append(place.place_id)
        result = []
        for place in places:
            if place.id not in occupied:
                result.append(place)
        if result == []:
            return None
        return result
    
    def reserve(db: Session, profile: int, flight: int, places: list[int]):
        autoverify = db.query(models.Global).get(1).autoverify
        if autoverify:
            flight_db = db.query(models.Flight).filter(models.Flight.id == flight).first()
            if flight_db:
                reservation = models.Reservation(profile=profile, flight=flight, price=flight_db.price, status="verified")
            else:
                return None
        else:
            flight_db = db.query(models.Flight).filter(models.Flight.id == flight).first()
            reservation = models.Reservation(profile=profile, flight=flight, price=flight_db.price, status="waiting")
        db.add(reservation)
        db.commit()
        db.refresh(reservation)
        reservations = db.query(models.Reservation).filter(models.Reservation.flight == flight, models.Reservation.status != "canceled").all()
        places_db = list(map(lambda x: x.id, db.query(models.Place).filter(models.Place.plane == flight_db.plane).all()))
        for place in places:
            if place not in places_db:
                return None
        print(places, places_db)
        occupied = []
        for reservation in reservations:
            for place in reservation.places:
                occupied.append(place.place_id)
        for place in places:
            if place not in occupied:
                reservation_place = models.Reservation_Place(reservation_id=reservation.id, place_id=place)
                db.add(reservation_place)
                db.commit()
                db.refresh(reservation_place)
        return {"result": "success"}

    def get_reservations(db: Session, profile: int) -> list:
        reservations = db.query(models.Reservation).filter(models.Reservation.profile == profile).all()
        result = []
        for reservation in reservations:
            if reservation:
                reservation = reservation.__dict__
            else:
                return None
            places = []
            for place in db.query(models.Reservation_Place).filter(models.Reservation_Place.reservation_id == reservation['id']).all():
                places.append(db.query(models.Place).filter(models.Place.id == place.place_id).first())
            reservation['places'] = places
            result.append(reservation)
        return result

    def get_reservation(db: Session, id: int, profile: int) -> dict:
        reservation = db.query(models.Reservation).filter(models.Reservation.id == id, models.Reservation.profile == profile).first()
        if reservation:
            reservation = reservation.__dict__
        else:
            return None
        places = []
        for place in db.query(models.Reservation_Place).filter(models.Reservation_Place.reservation_id == reservation['id']).all():
            places.append(db.query(models.Place).filter(models.Place.id == place.place_id).first())
        reservation['places'] = places
        return reservation

    def get_all_reservations(db: Session) -> list:
        reservations = db.query(models.Reservation).all()
        result = []
        for reservation in reservations:
            if reservation:
                reservation = reservation.__dict__
            else:
                return None
            places = []
            for place in db.query(models.Reservation_Place).filter(models.Reservation_Place.reservation_id == reservation['id']).all():
                places.append(db.query(models.Place).filter(models.Place.id == place.place_id).first())
            flight = db.query(models.Flight).filter(models.Flight.id == reservation['flight']).first().__dict__
            reservation['places'] = places
            reservation['flight'] = flight
            result.append(reservation)
        return result

    def cancel_reservation(db: Session, id: int, profile: int):
        reservation = db.query(models.Reservation).get(id)
        if reservation.profile == profile:
            reservation.status = "canceled"
            db.commit()
            return {"result": "success"}
        else:
            return {"error": "error"}

    def cancel_reservation_by_admin(db: Session, id: int):
        reservation = db.query(models.Reservation).get(id)
        if reservation:
            reservation.status = "canceled"
            db.commit()
            return True
        else:
            return None
    
    def confirm_reservation(db: Session, id: int):
        reservation = db.query(models.Reservation).get(id)
        if reservation:
            reservation.status = "verified"
            db.commit()
            return True
        else:
            return None

    def change_price(db: Session, id: int, price: float):
        flight = db.query(models.Flight).get(id)
        if flight:
            flight.price = price
            db.commit()
            return True
        else:
            return None

    def get_autoverify(db: Session) -> bool:
        return db.query(models.Global).get(1).autoverify

    def change_autoverify(db: Session) -> bool:
        autoverify = db.query(models.Global).get(1)
        autoverify.autoverify = not autoverify.autoverify
        db.commit()
        return autoverify.autoverify

    def get_price(db: Session, id: int) -> float:
        flight = db.query(models.Flight).filter(models.Flight.id == id).first()
        if flight:
            return flight.price
        else:
            return None

    def get_payment_link(db: Session, id: int, profile: int) -> str:
        reservation = db.query(models.Reservation).filter(models.Reservation.id == id, models.Reservation.profile == profile).first()
        if not reservation:
            return None
        return BASE_URL + '/booking/payment/' + str(reservation.return_url)
    
    def pay_reservation(db: Session, return_link: str):
        reservation = db.query(models.Reservation).filter(models.Reservation.return_url == return_link).first()
        reservation.status = 'paid'
        db.commit()

    def get_reservation_flight(db: Session, id: int) -> int:
        query = db.query(models.Reservation).filter(models.Reservation.id == id).first()
        if query:
            return query.flight
        else:
            return None

    def get_subs(db: Session, id: int) -> list:
        subscriptions = db.query(models.Subscription).filter(models.Subscription.flight == id).all()
        subs = []
        for subscription in subscriptions:
            subs.append(db.query(models.Auth).filter(models.Auth.user_id == subscription.profile).first().email)
        return subs
    
    def subscribe(db: Session, profile: id, flight: id):
        if db.query(models.Subscription).filter(models.Subscription.profile == profile, models.Subscription.flight == flight).first():
            return None
        if not db.query(models.Flight).filter(models.Flight.id == flight).first():
            return None
        subscription = models.Subscription(profile=profile, flight=flight)
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return True
