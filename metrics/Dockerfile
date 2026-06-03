FROM python:3.11-slim

WORKDIR /app

COPY metrics.py .

RUN pip install prometheus-client flask

CMD ["python", "metrics.py"]
