FROM python:3.11-slim

RUN apt-get update && apt-get install -y curl unzip && \
    curl -fsSL https://deno.land/install.sh | sh && \
    pip install flask yt-dlp requests

ENV PATH="/root/.deno/bin:$PATH"
ENV DENO_INSTALL="/root/.deno"

WORKDIR /app
COPY . .

EXPOSE 8080
CMD ["python", "main.py"]
Also update main.py — change the last line from:
pythonapp.run(host='0.0.0.0', port=port)
Change the port line to:
pythonport = int(os.environ.get('PORT', 8080))
app.run(host='0.0.0.0', port=port)
