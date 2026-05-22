FROM python:3.12-slim

WORKDIR /app

# Install dependencies first (layer cache)
COPY pyproject.toml .
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy source and install the package
COPY src/ src/
RUN pip3 install --no-cache-dir -e .

ENV PYTHONPATH=/app/src

EXPOSE 8000

CMD ["uvicorn", "tech_ziwei.main:app", "--host", "0.0.0.0", "--port", "8000"]
