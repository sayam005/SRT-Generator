# ——— Runtime ———
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-liberation \
    libjpeg62-turbo \
    zlib1g \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY backend/ .
RUN pip install --no-cache-dir -r requirements.txt

RUN mkdir -p temp jobs

RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 --ingroup appgroup appuser \
    && chown -R appuser:appgroup /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
