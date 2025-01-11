import pika
import json
import os
import logging
from io import StringIO
import pandas as pd
import pg8000

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5672")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PW = os.getenv("RABBITMQ_PW", "password")

QUEUE_NAME = "csv_chunks"

DBHOST = os.getenv('DBHOST', 'localhost')
DBUSERNAME = os.getenv('DBUSERNAME', 'myuser')
DBPASSWORD = os.getenv('DBPASSWORD', 'mypassword')
DBNAME = os.getenv('DBNAME', 'mydatabase')
DBPORT = os.getenv('DBPORT', '5432')


#Configure logging
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger()

reassembled_data= []

def process_message(ch,method,properties, body):
    str_stream = body.decode('utf-8')

    if str_stream == "__EOF__":
        print("EOF marker received. Finalizing...")
        file_content = b"".join(reassembled_data)
        csv_text = file_content.decode('utf-8')
        if len(reassembled_data) > 1:
            csvfile = StringIO(csv_text)
            df = pd.read_csv(csvfile)
            print(df)
            #call a function to save the df data to a database
        
        reassembled_data.clear()
    else:
        print(body)
        reassembled_data.append(body)

def main():
    credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PW)
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST,
    port=RABBITMQ_PORT, credentials=credentials))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)
    channel.basic_consume(queue=QUEUE_NAME,on_message_callback=process_message, auto_ack=True)
    logger.info(f"Waiting for messages...", exc_info=True)
    channel.start_consuming()

if __name__ == "__main__":
    main()