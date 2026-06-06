FROM python:3.11-slim
WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn httpx
COPY prvis/eol-mcp-server.py .
EXPOSE 8099
CMD ["uvicorn", "eol-mcp-server:app", "--host", "0.0.0.0", "--port", "8099"]
