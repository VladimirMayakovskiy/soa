FROM python:3.10-slim

WORKDIR /project/

COPY post_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY post_service/  post_service/
COPY proto/ proto/

COPY .env .env

ENV PYTHONPATH=/project:/project/proto

ENTRYPOINT ["python", "-m", "post_service.__main__"]