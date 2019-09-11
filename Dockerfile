FROM python:3.8-alpine
MAINTAINER Sofiane DERRAZ.
ENV PYTHONUNBUFFERED 1
RUN mkdir /todoapi
WORKDIR /todoapi
COPY . /todoapi
RUN apk add --update --no-cache postgresql-client
RUN apk add --update --no-cache --virtual .tmp-build-deps \
      gcc libc-dev linux-headers postgresql-dev \
      && apk add postgresql jpeg-dev zlib-dev libjpeg
RUN pip3 install -r /todoapi/requirements.txt
RUN apk del .tmp-build-deps
RUN adduser -D todoapi
USER todoapi