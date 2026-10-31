FROM python:3.12-slim

WORKDIR /app
RUN pip install --no-cache-dir httpx pydantic

COPY attack_runner.py /app/attack_runner.py

USER 1000:1000
CMD ["python", "attack_runner.py", "brute_force"]

