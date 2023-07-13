FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-alpine3.14

WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "${PYTHONPATH}:/app"

# copy requirements file
COPY requirements.txt /app/requirements.txt

# install dependencies
RUN set -eux \
    && apk add --no-cache --virtual .build-deps build-base postgresql-dev gcc libffi-dev libressl-dev musl-dev \
    && pip install -r /app/requirements.txt \
    && apk --purge del .build-deps build-base \
    && rm -rf /root/.cache/pip

# copy project
COPY app /app/app
COPY alembic.ini /app/alembic.ini
COPY alembic /app/alembic
