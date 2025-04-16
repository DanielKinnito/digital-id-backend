FROM digital-id-base:latest

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-dev --no-interaction

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 