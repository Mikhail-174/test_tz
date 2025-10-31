FROM python:3.14-alpine3.22

RUN apk update \
    && apk add --no-cache \
        postgresql-client \
        gcc \
        python3-dev \
        musl-dev \
        postgresql-dev \
    && rm -rf /var/cache/apk/*


WORKDIR /usr/src/workers

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .