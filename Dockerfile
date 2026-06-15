FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry

# Copia o arquivo que acabamos de criar para dentro do container
COPY pyproject.toml ./

# Instala as dependências pulando a criação de ambiente virtual interno (já que o container já é isolado)
RUN poetry config virtualenvs.create false && poetry install --no-root --no-interaction --no-ansi

# Copia todo o nosso código para dentro da pasta /app do container
COPY . .

EXPOSE 8080

# Comando ajustado indicando que a nossa API está dentro da pasta 'app'
CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]