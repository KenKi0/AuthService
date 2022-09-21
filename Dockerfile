FROM python:3.10

ARG PROJECT_ENV

WORKDIR /auth_service

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && \
    apt-get install -y libpq-dev wait-for-it && \
    apt-get clean

RUN pip install --no-cache-dir poetry==1.1.14

COPY poetry.lock poetry.lock
COPY pyproject.toml pyproject.toml

RUN poetry config virtualenvs.create false && \
    poetry install $(test "$PROJECT_ENV" = production && echo "--no-dev") --no-interaction --no-ansi

COPY src/ ./src
COPY tests ./tests
COPY .flake8 .flake8

CMD cd src && \
    export FLASK_APP=main.py && \
    flask db upgrade && \
    flask create_sudo $ADMIN_NAME $ADMIN_MAIL $ADMIN_PSWD && \
    flask create_tables && \
    python3 wsgi.py