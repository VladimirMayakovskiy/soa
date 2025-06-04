FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt ./requirements.txt

RUN apt-get update && \
    apt-get install -y gcc libpq-dev && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y --auto-remove gcc libpq-dev

WORKDIR /app

CMD ["pytest", "-vv", "--disable-warnings", "--maxfail=1"]
