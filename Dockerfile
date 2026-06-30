FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for ODBC
RUN apt-get update \
    && apt-get install -y curl apt-transport-https gnupg2 gcc g++ unixodbc-dev \
    && curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql18 \
    && apt-get clean

# Install Poetry
RUN pip install poetry

COPY pyproject.toml poetry.lock* /app/

# Disable virtualenv creation
RUN poetry config virtualenvs.create false \
  && poetry install --no-interaction --no-ansi --no-root

COPY . /app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
