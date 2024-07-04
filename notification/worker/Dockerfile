FROM python:3.10.8

RUN apt-get update && apt-get install -y netcat && rm -rf /var/lib/apt/lists/*
RUN pip install --upgrade pip

WORKDIR /worker

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip \
    && pip install -r requirements.txt


COPY . .
COPY wait_for_rabbit.sh /worker
RUN chmod +x ./wait_for_rabbit.sh

CMD ./wait_for_rabbit.sh rabbitmq:5672 && python worker.py