FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app ./app
RUN adduser --disabled-password --gecos '' app && mkdir -p /app/data && chown -R app:app /app
USER app
EXPOSE 8002
HEALTHCHECK --interval=30s --timeout=3s CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8002/health/live')"
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
