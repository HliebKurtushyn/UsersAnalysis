
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY web_app/ ./web_app/
COPY ml_pipeline/ ./ml_pipeline/
COPY artifacts/ ./artifacts/
COPY run.py .

EXPOSE 5000

CMD ["python", "run.py"]
