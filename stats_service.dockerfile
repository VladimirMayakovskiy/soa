FROM python:3.10-slim

WORKDIR /project/

COPY stats_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY stats_service/  stats_service/
COPY proto/ proto/

COPY .env .env

ENV PYTHONPATH=/project:/project/proto

ENTRYPOINT ["python", "-m", "stats_service.__main__"]