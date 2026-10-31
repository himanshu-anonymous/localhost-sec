FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic && \
    mkdir -p /var/log/aegis && chmod 777 /var/log/aegis

COPY web_target.py /app/web_target.py

EXPOSE 8080
USER 1000:1000
CMD ["uvicorn", "web_target:app", "--host", "0.0.0.0", "--port", "8080"]

