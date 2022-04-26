FROM python:3.10.3-alpine
MAINTAINER restlin1212

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

RUN pip install pipenv
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN apk add --update --no-cache postgresql-client jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps gcc libc-dev linux-headers postgresql-dev musl-dev zlib zlib-dev
RUN pipenv install --system --deploy
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D newuser
#RUN chown -R newuser:newuser /vol/
#RUN chmod -R 755 /vol/web
RUN chown -R newuser:newuser /app/
RUN chmod -R 755 /app
USER newuser
