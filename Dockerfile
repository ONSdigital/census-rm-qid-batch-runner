FROM python:3.7-slim

RUN pip install pipenv

RUN groupadd --gid 1000 qidbatchrunner && useradd --create-home --system --uid 1000 --gid qidbatchrunner qidbatchrunner
WORKDIR /home/qidbatchrunner

ENV RABBITMQ_SERVICE_HOST=rabbitmq
ENV RABBITMQ_SERVICE_PORT 5672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_QUEUE unaddressedRequestQueue
ENV RABBITMQ_USER rmquser
ENV RABBITMQ_PASSWORD rmqp455w0rd

COPY Pipfile* /home/qidbatchrunner/
RUN pipenv install --system --deploy
USER qidbatchrunner

RUN mkdir /home/qidbatchrunner/.postgresql

COPY --chown=qidbatchrunner . /home/qidbatchrunner