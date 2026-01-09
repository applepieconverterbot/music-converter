# 👇 CHANGED: Upgraded from 3.9 to 3.11 for yt-dlp compatibility
FROM python:3.11-slim

# Install FFmpeg AND Git
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Run the website
CMD gunicorn -w 4 -b 0.0.0.0:$PORT main:app
