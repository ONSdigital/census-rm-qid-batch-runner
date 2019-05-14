FROM python:3.6-slim

ENV RABBITMQ_HOST rabbitmq
ENV RABBITMQ_PORT 5672
ENV RABBITMQ_VHOST /
ENV RABBITMQ_QUEUE unaddressedRequestQueue
ENV RABBITMQ_USER guest
ENV RABBITMQ_PASSWORD guest

WORKDIR /app
COPY . /app
RUN pip install pipenv
RUN pipenv install --system --deploy