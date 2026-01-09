FROM python:3.11-slim

WORKDIR /app
COPY . .

# Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Run the website
CMD gunicorn -w 4 -b 0.0.0.0:$PORT main:app
