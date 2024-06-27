import smtplib, jinja2
from email.message import EmailMessage
from fastapi import Depends
from data import database, crud
from sqlalchemy.orm import Session
import datetime

from celery import Celery
from config import MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, REDIS_SERVER, BASE_URL
celery = Celery('tasks', broker=REDIS_SERVER, broker_connection_retry_on_startup=True)

jinja = jinja2.Environment()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Setup and call send_reminders() every 60 seconds.

    sender.add_periodic_task(60.0, send_subscription_remind_email, name='check reminders to be sent every minute')

@celery.task
def send_verification_email(address: str, id: str):
    email = EmailMessage()
    email["Subject"] = "Подтверди свою почту"
    email["From"] = MAIL_USERNAME
    email["To"] = address
    with open('templates/confirm.html', 'r') as file:
        template = jinja.from_string(file.read().rstrip())
    email.set_content(template.render(id=id, baseurl=BASE_URL).encode(), subtype='html', maintype='text')
    with smtplib.SMTP(MAIL_SERVER, 587) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(email)
        server.quit()

@celery.task
def send_restore_email(address: str, id: str):
    email = EmailMessage()
    email["Subject"] = "Подтверди сброс пароля"
    email["From"] = MAIL_USERNAME
    email["To"] = address
    with open('templates/restore.html', 'r') as file:
        template = jinja.from_string(file.read().rstrip())
    email.set_content(template.render(id=id, baseurl=BASE_URL).encode(), subtype='html', maintype='text')
    with smtplib.SMTP(MAIL_SERVER, 587) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(email)
        server.quit()

@celery.task
def send_password_email(address: str, password: str):
    email = EmailMessage()
    email["Subject"] = "Новый пароль"
    email["From"] = MAIL_USERNAME
    email["To"] = address
    with open('templates/password.html', 'r') as file:
        template = jinja.from_string(file.read().rstrip())
    email.set_content(template.render(password=password, baseurl=BASE_URL).encode(), subtype='html', maintype='text')
    with smtplib.SMTP(MAIL_SERVER, 587) as server:
        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.send_message(email)
        server.quit()

@celery.task
def send_subscription_price_email(addresses: list[str], id: str, old_price: float, new_price: float):
    for address in addresses:
        email = EmailMessage()
        email["Subject"] = "Цена поменялась!"
        email["From"] = MAIL_USERNAME
        email["To"] = address
        with open('templates/price.html', 'r') as file:
            template = jinja.from_string(file.read().rstrip())
        email.set_content(template.render(id=id, old=old_price, new=new_price, baseurl=BASE_URL).encode(), subtype='html', maintype='text')
        with smtplib.SMTP(MAIL_SERVER, 587) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(email)
            server.quit()

@celery.task
def send_subscription_place_email(addresses: list[str], id: str):
    for address in addresses:
        email = EmailMessage()
        email["Subject"] = "Еще есть места!"
        email["From"] = MAIL_USERNAME
        email["To"] = address
        with open('templates/place.html', 'r') as file:
            template = jinja.from_string(file.read().rstrip())
        email.set_content(template.render(id=id).encode(), subtype='html', maintype='text')
        with smtplib.SMTP(MAIL_SERVER, 587) as server:
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(email)
            server.quit()

@celery.task
def send_subscription_remind_email(db: Session = Depends(database.db_depends)):
    print("Sending remind emails")
    reservations = crud.Booking.get_all_reservations(db)
    for reservation in reservations:
        if reservation["flight"]["depatrureTime"] - datetime.datetime.now() <= datetime.timedelta(minutes=1) or True:
            email = EmailMessage()
            email["Subject"] = "Не забудь улететь!"
            email["From"] = MAIL_USERNAME
            email["To"] = crud.Auth.get_email_by_profile(db, reservation["profile"])
            with open('templates/remind.html', 'r') as file:
                template = jinja.from_string(file.read().rstrip())
            email.set_content(template.render(id=id, time=reservation["flight"]["depatrureTime"], baseurl=BASE_URL).encode(), subtype='html', maintype='text')
            with smtplib.SMTP(MAIL_SERVER, 587) as server:
                server.login(MAIL_USERNAME, MAIL_PASSWORD)
                server.send_message(email)
                server.quit()

celery.conf.beat_schedule = {
    'run-me-every-ten-seconds': {
        'task': 'tasks.send_subscription_remind_email',
        'schedule': 10.0
    }
}