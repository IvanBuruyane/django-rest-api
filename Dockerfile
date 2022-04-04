FROM python
MAINTAINER restlin1212

ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=app.settings

RUN pip install pipenv
COPY ./Pipfile /Pipfile
COPY ./Pipfile.lock /Pipfile.lock
RUN apt-get install postgresql
RUN apt-get install .tmp-build-deps gcc libc-dev linux-headers postgresql-dev
RUN pipenv install --system --deploy
#RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D newuser
USER newuser
