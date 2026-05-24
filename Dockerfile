FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt pyproject.toml README.md Dockerfile .dockerignore ./
COPY src ./src

RUN python -m pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install -e .

COPY tests ./tests
COPY app ./app
COPY docs ./docs
COPY reports ./reports

CMD ["python", "-m", "pytest"]
