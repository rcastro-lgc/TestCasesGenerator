FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Create data directory if it doesn't exist
RUN mkdir -p /data

EXPOSE 5000

CMD ["python", "run_ui.py"]
