FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir fastapi uvicorn pydantic

COPY agent.py /app/agent.py

EXPOSE 8090
CMD ["uvicorn", "agent:app", "--host", "0.0.0.0", "--port", "8090"]

