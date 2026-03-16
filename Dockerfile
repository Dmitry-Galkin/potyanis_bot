FROM python:3.14-slim
WORKDIR /potyanis_bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN mkdir -p /potyanis_bot/data
CMD ["python", "main.py"]
