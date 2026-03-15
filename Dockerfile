FROM python:3.14-slim
WORKDIR /potyanis_bot
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "main.py"]
