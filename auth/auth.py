from fastapi import APIRouter, Depends, status, BackgroundTasks, Form
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy.orm import Session
from auth import jwt_handler, hash, jwt_bearer
from data import crud, database, schemas
from tasks.tasks import send_password_email, send_restore_email, send_verification_email
import re, datetime, random, string

AuthRouter = APIRouter(prefix='/auth')

@AuthRouter.post('/login')
async def login(auth: schemas.Auth, db: Session = Depends(database.db_depends)):
    """
    Авторизация пользователя по почте и паролю. Возвращает JWT-токены для дальнейших запросов
    """
    if not crud.Auth.user_exists(db, auth.email):
        return JSONResponse({"error":"invalid user"}, status.HTTP_401_UNAUTHORIZED)
    if not hash.verify(auth.password, crud.Auth.get_hashed(db, auth.email)):
        return JSONResponse({"error":"invalid user"}, status.HTTP_401_UNAUTHORIZED)
    if not crud.Auth.verified_email(db, auth.email):
        return JSONResponse({"error":"invalid user"}, status.HTTP_401_UNAUTHORIZED)
    return {"access_token": jwt_handler.access_token(crud.Auth.get_profile_id(db, auth.email), crud.Auth.get_role(db, auth.email)),
            "refresh_token": jwt_handler.refresh_token(crud.Auth.get_profile_id(db, auth.email), crud.Auth.get_role(db, auth.email))
            }

@AuthRouter.get("/refresh", tags=["Аутентификация"], responses={
    200: {"description": "Токены обновлены", "content": {
        "application/json": {
            "example": {"access_token": "access token",
                        "refresh_token": "refresh token"}
        }
    }}
})
async def refresh(token = Depends(jwt_bearer.JWTRefreshBearer())):
    """
    Обновление access token и refresh token. Требуется авторизация по refresh token через заголовок Authorization: Bearer TOKEN
    """
    return {"access_token": jwt_handler.access_token(jwt_handler.refresh_decode(token)['id'], jwt_handler.refresh_decode(token)['role']),
            "refresh_token": jwt_handler.refresh_token(jwt_handler.refresh_decode(token)['id'], jwt_handler.refresh_decode(token)['role'])}

@AuthRouter.post('/register')
async def registation(background_tasks: BackgroundTasks, profile: schemas.ProfileCreate, auth: schemas.AuthCreate, db: Session = Depends(database.db_depends)):
    """
    Регистрация пользователя. После регистрации на указанную почту отправляется письмо с ссылкой на подтверждение (см. /verify) 
    Для успешной регистрации поля должны соответствовать следующим требованиям:
    1. Почта должна соответствовать обычному формату
    2. Почта не должна быть уже зарегистрирована на другого пользователя
    3. Пароль должен содержать хотя бы одну цифру, одну английскую букву, и быть длиной не менее 8 символов
    """
    if not re.match(r"\S+@\S+\.\S+" , auth.email):
        return JSONResponse({"error": "invalid email"}, status.HTTP_400_BAD_REQUEST)
    if crud.Auth.user_exists(db, auth.email):
        return JSONResponse({"error": "user exists"}, status.HTTP_401_UNAUTHORIZED)
    if sum(symbol.isdigit() for symbol in auth.password) == 0 or len(auth.password) < 8 or sum(symbol.isalpha() for symbol in auth.password) == 0:
        return JSONResponse({"error": "invalid password"}, status.HTTP_400_BAD_REQUEST)
    db_profile = crud.Auth.create_profile(db, profile)
    db_auth = crud.Auth.create_auth(db, auth, db_profile.id)
    background_tasks.add_task(send_verification_email, auth.email, db_auth.id)
    return {"result": "success"}

@AuthRouter.get('/verify/{id}')
async def email_verification(background_tasks: BackgroundTasks, id: str, restore: bool = False, db: Session = Depends(database.db_depends)):
    """
    Запрос посылается от пользователя при переходе по ссылке из письма (см. /register)
    Возвращает HTML с текстом о статусе подтверждения или восстановления
    """
    try:
        if crud.Auth.get_auth(db, id):
            if restore:
                generated = ''.join(random.choice(string.ascii_letters + string.digits) for i in range(8))
                crud.Auth.change_password(db, id, generated)
                background_tasks.add_task(send_password_email, crud.Auth.get_email(db, id), generated)
                return HTMLResponse("""Пароль отправлен на почту""", status.HTTP_200_OK)
            if not crud.Auth.verified(db, id):
                crud.Auth.verify(db, id)
                return HTMLResponse("""Электронная почта подтверждена""", status.HTTP_200_OK)
    except:
        return HTMLResponse("""Неправильная ссылка""", status.HTTP_400_BAD_REQUEST)
    return HTMLResponse("""Неправильная ссылка""", status.HTTP_400_BAD_REQUEST)

@AuthRouter.get('/resend')
async def resend_verification(background_tasks: BackgroundTasks, email: str, db: Session = Depends(database.db_depends)):
    """
    Запрос повторной отправки письма для подтверждения на почту. Можно вызвать только раз в 45 секунд.
    """
    if not crud.Auth.user_exists(db, email):
        return {"result": "success"}
    if crud.Auth.verified_email(db, email):
        return {"result": "success"}
    if (datetime.datetime.today() - crud.Auth.get_sent(db, email)).total_seconds() < 45:
        return JSONResponse({"error": "timeout"}, status.HTTP_425_TOO_EARLY)
    crud.Auth.change_sent(db, email, datetime.datetime.today())
    background_tasks.add_task(send_verification_email, email, crud.Auth.get_id(db, email))
    return {"result": "success"}

@AuthRouter.get('/restore')
async def send_restore(background_tasks: BackgroundTasks, mail: str, db: Session = Depends(database.db_depends)):
    """
    Запрос отправки письма для восстановления пароля на почту. Можно вызвать только раз в 45 секунд.
    """
    if not crud.Auth.user_exists(db, mail):
        return {"result": "success"}
    if (datetime.datetime.today() - crud.Auth.get_sent(db, mail)).total_seconds() < 45:
        return JSONResponse({"error": "timeout"}, status.HTTP_425_TOO_EARLY)
    crud.Auth.change_sent(db, mail, datetime.datetime.today())
    background_tasks.add_task(send_restore_email, mail, crud.Auth.create_auth_id(db, mail))
    return {"result": "success"}