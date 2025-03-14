FROM python:3.12
ENV PIPX_BIN_DIR=/root/.local/bin
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    PATH=${PIPX_BIN_DIR}:${PATH}
RUN apt-get update && apt-get install -y pipx && pipx ensurepath && pipx install poetry
WORKDIR /app
COPY pyproject.toml poetry.lock README.md .
RUN poetry install --no-root && poetry run playwright install chromium && poetry run playwright install-deps
COPY . .
RUN poetry install --only-root
CMD ["poetry", "run", "fastapi", "run", "simula_ligths_api/api.py", "--host", "0.0.0.0"]
