FROM python:3.10-slim

RUN apt-get update && apt-get install -y curl
RUN curl -sSL "https://github.com/fullstorydev/grpcurl/releases/download/v1.8.7/grpcurl_1.8.7_linux_x86_64.tar.gz" | tar -xz -C /usr/local/bin

WORKDIR /project

COPY tests/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install pytest pytest-asyncio

COPY tests/*.py tests/

COPY proto/posts.proto proto/posts.proto
COPY proto/posts_pb2.py proto/posts_pb2.py
COPY proto/posts_pb2_grpc.py proto/posts_pb2_grpc.py

ENV PYTHONPATH=/project:/project/proto

ENTRYPOINT ["pytest", "-vs", "-p", "no:warnings", "tests/"]