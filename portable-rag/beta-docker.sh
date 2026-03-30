docker run --name beta-portable-rag -v .:/app -v ./beta.env:/app/.env -w /app -it -p 127.0.0.1:23354:8501 -d --restart=unless-stopped python:3-slim ./run-webui.sh
