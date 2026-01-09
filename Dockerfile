FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir -r requirements.txt
CMD gunicorn -w 4 -b 0.0.0.0:$PORT main:app
