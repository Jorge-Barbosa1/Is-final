FROM python:3.9-slim
RUN pip install --upgrade pip
WORKDIR /app
COPY . /app/

# Add the grpc folder to the PYTHONPATH because was not recognizing the grpc module
ENV PYTHONPATH="${PYTHONPATH}:/app/api/grpc"

RUN pip install --no-cache-dir --timeout=180 -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
