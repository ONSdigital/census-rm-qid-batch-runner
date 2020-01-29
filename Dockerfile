FROM python:3.7-slim

RUN pip install pipenv

RUN groupadd --gid 1000 qidbatchrunner && useradd --create-home --system --uid 1000 --gid qidbatchrunner qidbatchrunner
WORKDIR /home/qidbatchrunner

ENV RABBITMQ_SERVICE_HOST=rabbitmq
ENV RABBITMQ_SERVICE_PORT 5672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_QUEUE unaddressedRequestQueue
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

COPY Pipfile* /home/qidbatchrunner/
RUN pipenv install --system --deploy
USER qidbatchrunner

COPY --chown=qidbatchrunner . /home/qidbatchrunner