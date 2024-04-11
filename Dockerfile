# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder

RUN apk update && apk add --no-cache supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

WORKDIR /app

COPY requirements.txt /app
RUN pip3 install -r requirements.txt

COPY . /app

# ENTRYPOINT ["python3"]
# CMD ["app.py"]
CMD ["/usr/bin/supervisord"]