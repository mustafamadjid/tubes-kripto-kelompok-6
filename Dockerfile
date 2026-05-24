FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN groupadd --system app && useradd --system --gid app --home-dir /app app \
    && mkdir -p /data/keys \
    && chown -R app:app /app /data

USER app

EXPOSE 8000
ENTRYPOINT ["sh", "./scripts/docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
