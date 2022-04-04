FROM python:3.10.3-alpine
MAINTAINER restlin1212

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

RUN pip install pipenv
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN apk add --update --no-cache postgresql
RUN apk add --update --no-cache docker-compose
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers postgresql-dev
RUN pipenv install --system --deploy
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D newuser
USER newuser
