FROM digital-id-base:latest

# Install additional dependencies for fingerprint scanning
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libusb-1.0-0 \
        libfprint-2-2 \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"] 
# uvicorn app.main:app --reload --port 8001 --- for app start