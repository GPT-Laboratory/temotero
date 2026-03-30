docker run --name portable-rag -v .:/app -w /app -it -p 127.0.0.1:33354:8501 -d --restart=unless-stopped python:3-slim ./run-webui.sh
