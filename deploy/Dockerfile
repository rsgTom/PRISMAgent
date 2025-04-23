FROM python:3.10-slim as base

WORKDIR /app

# Setup Python environment
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=100

# Install Poetry for dependency management
RUN pip install poetry

# Copy only dependencies first for better caching
COPY pyproject.toml ./

# Configure Poetry to not use a virtual environment in the container
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-dev

# Development stage
FROM base as development
WORKDIR /app
COPY . .
RUN poetry install --no-interaction --no-ansi

# Production stage for API
FROM base as api
WORKDIR /app
COPY . .

EXPOSE 8000
CMD ["python", "-m", "PRISMAgent.ui.api.fastapi_app"]

# Production stage for Streamlit
FROM base as streamlit
WORKDIR /app
COPY . .

EXPOSE 8501
CMD ["streamlit", "run", "PRISMAgent/ui/streamlit_app/main.py"] 