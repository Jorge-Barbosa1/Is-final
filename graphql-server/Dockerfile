FROM python:3.9-slim

# Instalar dependências básicas
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Instalar dependências do GraphQL
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o código
COPY . /app

# Porta padrão para o GraphQL
EXPOSE 9000

# Comando para rodar o servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:9000"]
