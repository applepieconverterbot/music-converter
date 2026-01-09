FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start the server
CMD gunicorn -w 4 -b 0.0.0.0:$PORT main:app
