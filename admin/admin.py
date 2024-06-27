from fastapi import APIRouter, Depends, status, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from auth import jwt_handler, jwt_bearer
from data import crud, database
from tasks.tasks import send_subscription_price_email, send_subscription_place_email 

AdminRouter = APIRouter(prefix='/admin')

@AdminRouter.get('/reservations')
async def get_reservations(db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        return crud.Booking.get_all_reservations(db)
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)

@AdminRouter.patch('/reservation')
async def confirm_reservation(reservation: int, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        query = crud.Booking.confirm_reservation(db, reservation)
        if not query:
            return JSONResponse({"error": "reservation not found"}, status.HTTP_404_NOT_FOUND)
        return {"result": "success"}
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)
    
@AdminRouter.delete('/reservation')
async def cancel_reservation(background_tasks: BackgroundTasks, reservation: int, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        query = crud.Booking.cancel_reservation_by_admin(db, reservation)
        if not query:
            return JSONResponse({"error": "reservation not found"}, status.HTTP_404_NOT_FOUND)
        flight = crud.Booking.get_reservation_flight(db, reservation)
        background_tasks.add_task(send_subscription_place_email, crud.Booking.get_subs(db, flight), flight)
        return {"result": "success"}
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)

@AdminRouter.get('/autoverify')
async def get_autoverify(db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        return crud.Booking.get_autoverify(db)
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)
    
@AdminRouter.patch('/autoverify')
async def change_autoverify(db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        return crud.Booking.change_autoverify(db)
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)
    
@AdminRouter.patch('/flight')
async def change_price(background_tasks: BackgroundTasks, flight: int, price: float, db: Session = Depends(database.db_depends), token = Depends(jwt_bearer.JWTAccessBearer())):
    if jwt_handler.access_decode(token)['role'] == "admin":
        old_price = crud.Booking.get_price(db, flight)
        if not old_price:
            return JSONResponse({"error": "flight not found"}, status.HTTP_404_NOT_FOUND)
        query = crud.Booking.change_price(db, flight, price)
        if not query:
            return JSONResponse({"error": "flight not found"}, status.HTTP_404_NOT_FOUND)
        background_tasks.add_task(send_subscription_price_email, crud.Booking.get_subs(db, flight), flight, old_price, price)
        return {"result": "success"}
    else:
        return JSONResponse({"error": "no access"}, status.HTTP_403_FORBIDDEN)