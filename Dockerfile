FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /srv/kudu
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && useradd --system --uid 10001 kudu \
    && mkdir -p /data && chown kudu:kudu /data
COPY app ./app
COPY web ./web
USER kudu
ENV KUDU_DATABASE_PATH=/data/kudu.sqlite3 KUDU_WORKSPACE_ROOT=/data/workspaces
EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]
