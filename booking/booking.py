from fastapi import APIRouter, Depends, BackgroundTasks, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth import jwt_bearer, jwt_handler
from data import crud, database, schemas
from tasks.tasks import send_subscription_place_email

BookingRouter = APIRouter(prefix='/booking')

@BookingRouter.get('/get')
async def get_flights(db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    return crud.Booking.get_flights(db)

@BookingRouter.post('/reserve')
async def reserve(book: schemas.Book, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    query = crud.Booking.reserve(db, jwt_handler.access_decode(token)['id'], book.flight, book.places)
    if not query: 
        return JSONResponse({"error": "flight or places not found"}, status.HTTP_404_NOT_FOUND)
    return {"result": "success"}

@BookingRouter.get('/reservation')
async def get_reservation(reservation: int, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    query = crud.Booking.get_reservation(db, reservation, jwt_handler.access_decode(token)['id'])
    if not query:
        return JSONResponse({"error": "reservation not found"}, status.HTTP_404_NOT_FOUND)
    return query

@BookingRouter.get('/reservations')
async def get_reservations(db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    return crud.Booking.get_reservations(db, jwt_handler.access_decode(token)['id'])

@BookingRouter.delete('/reservation')
async def cancel_reservation(background_tasks: BackgroundTasks, reservation: int, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    flight = crud.Booking.get_reservation_flight(db, reservation)
    if not flight:
        return JSONResponse({"error": "reservation not found"}, status.HTTP_404_NOT_FOUND)
    background_tasks.add_task(send_subscription_place_email, crud.Booking.get_subs(db, flight), reservation)
    return crud.Booking.cancel_reservation(db, reservation, jwt_handler.access_decode(token)['id'])

@BookingRouter.get('/pay')
async def pay_for_reservation(reservation: int, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    query = crud.Booking.get_payment_link(db, reservation, jwt_handler.access_decode(token)['id'])
    if not query:
        return JSONResponse({"error": "reservation not found"}, status.HTTP_404_NOT_FOUND)
    return query

@BookingRouter.get('/payment/{id}')
async def return_url(id: str, db: Session = Depends(database.db_depends)):
    crud.Booking.pay_reservation(db, id)
    return {"result": "success"}

@BookingRouter.get('/subscribe')
async def subscribe_to_flight(flight: str, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    query = crud.Booking.subscribe(db, jwt_handler.access_decode(token)['id'], flight)
    if not query:
        return JSONResponse({"error": "flight not found"}, status.HTTP_404_NOT_FOUND)
    return {"result": "success"}