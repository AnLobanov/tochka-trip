FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY . . 

RUN pip install --no-cache-dir --upgrade -r requirements.txt

ARG MAIL_USERNAME
ENV MAIL_USERNAME ${MAIL_USERNAME}
ARG MAIL_PASSWORD
ENV MAIL_PASSWORD ${MAIL_PASSWORD}
ARG MAIL_FROM
ENV MAIL_FROM ${MAIL_FROM}
ARG MAIL_SERVER
ENV MAIL_SERVER ${MAIL_SERVER}
ARG JWT_ACCESS_SECRET
ENV JWT_ACCESS_SECRET ${JWT_ACCESS_SECRET}
ARG JWT_REFRESH_SECRET
ENV JWT_REFRESH_SECRET ${JWT_REFRESH_SECRET}
ARG JWT_ALGORITHM
ENV JWT_ALGORITHM ${JWT_ALGORITHM}
ARG JWT_ACCESS_MINUTES
ENV JWT_ACCESS_MINUTES ${JWT_ACCESS_MINUTES}
ARG JWT_REFRESH_DAYS
ENV JWT_REFRESH_DAYS ${JWT_REFRESH_DAYS}
ARG DB_NAME
ARG DB_USER
ARG DB_PASSWORD
ENV DB_SERVER="postgresql+psycopg2://${DB_USER}:${DB_PASSWORD}@postgres/${DB_NAME}"
ARG REDIS_SERVER
ENV REDIS_SERVER=${REDIS_SERVER}
ARG BASE_URL
ENV BASE_URL=${BASE_URL}

RUN alembic init data/migrations
RUN alembic revision --autogenerate -m "init"
RUN alembic upgrade head
ENTRYPOINT celery -A tasks.tasks:celery worker --loglevel=INFO --pool=solo