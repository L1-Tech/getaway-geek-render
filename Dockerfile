FROM python:3.10-slim

RUN apt-get update &&     apt-get install -y ffmpeg &&     pip install fastapi uvicorn

COPY . /app
WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]