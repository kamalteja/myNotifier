ARG PROJECT=slack_bot
ARG APP_PATH=/opt/app/${PROJECT}

FROM python:3.11 as slack_bot

ARG APP_PATH
ARG PROJECT

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get upgrade -y
RUN pip install --upgrade pip

WORKDIR ${APP_PATH}

# Installing code
COPY notifier/ notifier/
COPY pyproject.toml pyproject.toml
COPY readme.md readme.md
COPY makefile makefile
RUN make install

FROM nginx:latest as nginx

ARG PROJECT
ARG APP_PATH

RUN apt-get update && apt-get upgrade -y

RUN mv /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.back
COPY docker/slack-bot.nginx.conf /etc/nginx/conf.d/
