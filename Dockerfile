FROM python:3.12-alpine

WORKDIR /app

RUN apk add git
# Установка Poetry и UV
RUN pip install --no-cache-dir uv

# Сначала копируем файлы pyproject.toml и README.md
COPY pyproject.toml README.md ./

# Выполняем uv sync (он должен видеть pyproject.toml)
RUN uv sync --no-dev

# Копируем весь проект
COPY . .


ENV PYTHONPATH=/app

CMD ["uv", "run", "python", "-m", "src.main"]