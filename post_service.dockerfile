FROM python:3.10-slim

WORKDIR /project/

COPY post_service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest

COPY post_service/  post_service/
COPY proto/ proto/

ENV PYTHONPATH=/project:/project/proto

ENTRYPOINT ["python", "-m", "post_service.main"]