FROM python:3.10.3-alpine
MAINTAINER restlin1212

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

RUN pip install pipenv
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN pipenv install --system --deploy

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D newuser
USER newuser
