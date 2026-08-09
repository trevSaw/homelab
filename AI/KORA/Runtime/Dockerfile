FROM python:3.12-slim-bookworm

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    KORA_CONFIG_DIR=/config \
    KORA_PROMPTS_DIR=/prompts

COPY Runtime/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY Runtime/app ./app
COPY Knowledge ./Knowledge
COPY Tools ./Tools

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --retries=5 --start-period=20s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=3)"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
