# Dockerfile
FROM python:3.10.4-slim-buster
RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt . 

RUN pip install --no-cache-dir -r requirements.txt

COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh
ENTRYPOINT ["docker-entrypoint.sh"]