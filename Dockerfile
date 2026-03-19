FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl unzip ffmpeg && \
    curl -fsSL https://deno.land/install.sh | sh && \
    pip install flask yt-dlp requests

ENV PATH="/root/.deno/bin:$PATH"
ENV DENO_INSTALL="/root/.deno"

WORKDIR /app
COPY . .

EXPOSE 8080
CMD ["python", "main.py"]
