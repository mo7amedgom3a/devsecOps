# Intentionally using an outdated, unsupported base image
FROM python:3.6-slim-stretch

WORKDIR /app

COPY requirements.txt .

# Install the vulnerable dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8080

CMD ["python", "app.py"]
