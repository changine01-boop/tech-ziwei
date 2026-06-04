FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml .
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source and install the package
COPY src/ src/
COPY alembic/ alembic/
COPY alembic.ini .
COPY entrypoint.sh .
RUN pip3 install --no-cache-dir -e . && chmod +x /app/entrypoint.sh

ENV PYTHONPATH=/app/src

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
