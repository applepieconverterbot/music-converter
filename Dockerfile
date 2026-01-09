FROM python:3.9-slim

# Install FFmpeg AND Git (Git is required to download the latest yt-dlp)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . .

# Install Python libraries
RUN pip install --no-cache-dir -r requirements.txt

# Run the website
CMD gunicorn -w 4 -b 0.0.0.0:$PORT main:app
