from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from auth.auth import AuthRouter
from fastapi import applications
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.middleware.cors import CORSMiddleware
from data.database import db_init, db_depends, engine
from data.crud import init_mock
from booking.booking import BookingRouter
from admin.admin import AdminRouter
from os import environ

tags = [
    {
        "name": "Первая домашка",
        "description": "Всякие хеллоу, эхо, и прочие пинг-понги"
    },
    {
        "name": "Аутентификация",
        "description": "Авторизация и регистрация пользователя"
    },
    {
        "name": "Бронирование",
        "description": "Система бронирования билетов на самолет"
    },
    {
        "name": "Администрирование",
        "description": "Администрирование системы бронирования. You should not pass!"
    }
]

app = FastAPI(title="Точка Трип API",
              description="В командировку с комфортом",
              version="0.0.1",
              openapi_tags=tags,
              root_path='/' + environ["BASE_URL"].split('/')[-1])
app.include_router(AuthRouter, tags=["Аутентификация"])
app.include_router(BookingRouter, tags=["Бронирование"])
app.include_router(AdminRouter, tags=["Администрирование"])

origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

if environ["TEST"] == "FALSE":
    db_init()

def swagger_monkey_patch(*args, **kwargs):
    return get_swagger_ui_html(
        *args, **kwargs,
        swagger_js_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui-bundle.min.js",
        swagger_css_url="https://cdn.staticfile.net/swagger-ui/5.1.0/swagger-ui.min.css")

applications.get_swagger_ui_html = swagger_monkey_patch

@app.on_event("startup")
async def startup():
    connection = engine.connect()
    db = Session(bind=connection)
    init_mock(db)

@app.get('/echo', tags=["Первая домашка"], responses={
    200: {"description": "Все заголовки входящего запроса", "content": {
        "application/json": {
            "example": {
            "host": "127.0.0.1:8000",
            "connection": "keep-alive",
            "sec-ch-ua": "\"Google Chrome\";v=\"125\", \"Chromium\";v=\"125\", \"Not.A/Brand\";v=\"24\"",
            "accept": "application/json",
            "sec-ch-ua-mobile": "?0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-site": "same-origin",
            "sec-fetch-mode": "cors",
            "sec-fetch-dest": "empty",
            "referer": "http://127.0.0.1:8000/docs",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
            }
        }
    }}
})
async def get_headers(request: Request):
    """
    Выдает все заголовки входящего запроса
    """
    return request.headers

@app.post('/echo', tags=["Первая домашка"], responses={
    200: {"description": "Тело запроса", "content": {
        "application/json": {"example": "ping"}
    }}
})
async def get_body(request: Request):
    """
    Возвращает переданное тело запроса
    """
    return await request.body()

@app.get('/hello', tags=["Первая домашка"], responses={
    200: {"description": "Поздоровался", "content": {
        "application/json": {"example": "hello"}
    }}
})
async def say_hello():
    """
    Отвечает на запрос строкой "hello"
    """
    return "hello"