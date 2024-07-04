FROM python:3.9-slim

WORKDIR /admin
RUN mkdir -p /admin/static/ \
    && mkdir -p /admin/media/ \
    && groupadd -r usr \
    && useradd -d /admin/ -r -g usr usr \
    && chown usr:usr -R /admin/ \
    && apt-get update \
    && apt-get -y install libpq-dev gcc

COPY wait-for-it.sh /admin/
RUN chmod +x ./wait-for-it.sh

RUN pip install --upgrade pip
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000
CMD ./wait-for-it.sh ${POSTGRES_HOST}:${POSTGRES_PORT} \
    && python manage.py collectstatic --noinput \
    && python manage.py migrate \
    && gunicorn config.wsgi --bind 0.0.0.0:8000 --reload
