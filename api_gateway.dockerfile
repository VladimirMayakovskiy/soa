FROM python:3.10-slim

WORKDIR /project/

COPY api_gateway/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest

COPY api_gateway/ api_gateway/
COPY proto/ proto/

ENV PYTHONPATH=/project:/project/proto

CMD ["uvicorn", "api_gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
