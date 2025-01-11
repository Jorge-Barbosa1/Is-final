#Base image
From python:3.10-slim

RUN pip install --upgrade pip

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

# Copia tudo
COPY . . 

EXPOSE 50051

CMD ["python", "main.py"]
