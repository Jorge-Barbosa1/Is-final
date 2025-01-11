import csv
import sys
import xml.etree.ElementTree as ET
import requests
from concurrent import futures
from settings import GRPC_SERVER_PORT, MAX_WORKERS, MEDIA_PATH, DBNAME, DBUSERNAME, DBPASSWORD, DBHOST, DBPORT
from settings import RABBITMQ_HOST, RABBITMQ_PORT, RABBITMQ_USER, RABBITMQ_PW
import os
import grpc
import logging
import pg8000
import server_services_pb2
import server_services_pb2_grpc
import pika
from server_services_pb2 import CsvToXmlResponse, SendFileResponseBody, SendFileChunksResponse ,XmlFilterResponse
from server_services_pb2_grpc import SendFileServiceServicer, add_SendFileServiceServicer_to_server

from geopy.geocoders import Nominatim
import uuid #Generate unique IDs for XML elements
import xml.sax.saxutils as saxutils
from lxml import etree

#Configura logging
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger= logging.getLogger("FileService")

#XSL Path   
XSD_PATH = os.path.join(MEDIA_PATH, "schema.xsd")

#Aumenta o limite de tamanho de campo do CSV
csv.field_size_limit(sys.maxsize)

#Classe que implementa os métodos do serviço gRPC
class SendFileService(SendFileServiceServicer):

    def __init__(self, *args, **kwargs):
        if not os.path.exists(XSD_PATH):
            raise FileNotFoundError(f"XSD not found: {XSD_PATH}")
        with open(XSD_PATH, 'r') as xsd_file:
            schema_root = etree.XML(xsd_file.read())
            logging.info(f"XSD Schema found {schema_root.tag}")
        self.schema = etree.XMLSchema(schema_root)

    #Método que recebe o arquivo CSV e retorna o XML.Usa a API Nominatim para obter latitude e longitude
    def ProcessCsvToXml(self, request, context):
        locator = Nominatim(user_agent="myGeocoder")

        try:
            csv_content = request.csv_file.decode('utf-8').splitlines()
            reader = csv.DictReader(csv_content)

            root = ET.Element("Data")
            for row in reader:
                item = ET.SubElement(root, "Item", ID=str(uuid.uuid4()))  # Adiciona um ID único
                for key, value in row.items():
                    # Remover caracteres inválidos de tags
                    key_cleaned = key.replace(" ", "_").replace("%", "")
                    element = ET.SubElement(item, key_cleaned)
                    element.text = value

                # Adiciona localização se houver uma cidade
                location = row.get("City", "").strip()
                if location:
                    try:
                        response = requests.get(
                            "https://nominatim.openstreetmap.org/search",
                            params={"q": location, "format": "json"},
                            timeout=10  # Aumenta o timeout se necessário
                        )
                        if response.status_code == 200 and response.json():
                            coords = response.json()[0]
                            ET.SubElement(item, "Latitude").text = coords.get("lat", "N/A")
                            ET.SubElement(item, "Longitude").text = coords.get("lon", "N/A")
                    except requests.RequestException as e:
                        logging.error(f"Error accesing API {location}: {e}")
                        ET.SubElement(item, "Latitude").text = "N/A"
                        ET.SubElement(item, "Longitude").text = "N/A"

            # Gera o conteúdo XML
            xml_content = ET.tostring(root, encoding="utf-8").decode("utf-8")
            return CsvToXmlResponse(xml_content=xml_content)
        except Exception as e:
            logging.error(f"Error processing: {e}")
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return CsvToXmlResponse(xml_content="")

    def ValidateXml(self, request, context):
        try:
            # Recebe o XML do request
            xml_content = request.xml_file.decode("utf-8")
        
            xml_doc = etree.fromstring(xml_content)
            
            self.schema.assertValid(xml_doc)
            
            return server_services_pb2.CsvToXmlResponse(
                xml_content=etree.tostring(xml_doc, pretty_print=True, encoding="utf-8").decode("utf-8"),
                message="XML is valid"
            )
        except etree.DocumentInvalid as e:
            logging.error(f"XML Validation Error: {e}")
            context.set_details(f"XML Validation Error: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return server_services_pb2.CsvToXmlResponse(
                xml_content="", 
                message="XML is not valid"
            )
        except Exception as e:
            logging.error(f"Unexpected error during XML validation: {e}")
            context.set_details(f"Unexpected Error: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.CsvToXmlResponse(
                xml_content="", 
                message="An unexpected error occurred"
            )

    def FilterXml(self, request, context):
        try:
            # Caminho completo do arquivo XML
            file_path = os.path.join(MEDIA_PATH, request.file_name)
            if not os.path.exists(file_path):
                context.set_details(f"Arquivo {request.file_name} não encontrado")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return XmlFilterResponse(
                    results=[],
                    message="Arquivo não encontrado"
                )

            # Carregar e processar o XML
            tree = etree.parse(file_path)

            # Executar a consulta XPath
            results = tree.xpath(request.xpath_query)

            # Processar os resultados
            response_data = []
            for result in results:
                if isinstance(result, etree._Element):  # Se o resultado for um nó XML
                    response_data.append(etree.tostring(result, pretty_print=True, encoding="unicode"))
                else:
                    response_data.append(str(result))

            return XmlFilterResponse(
                results=response_data,
                message="Consulta executada com sucesso"
            )
        except etree.XPathError as e:
            context.set_details(f"Erro na consulta XPath: {e}")
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            return XmlFilterResponse(
                results=[],
                message="Erro na consulta XPath"
            )
        except Exception as e:
            context.set_details(f"Erro inesperado: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return XmlFilterResponse(
                results=[],
                message="Erro inesperado"
            )

    def ExportToDatabase(self, request, context):
        try:
            file_path = os.path.join(MEDIA_PATH, request.file_name)
            if not os.path.exists(file_path):
                context.set_details(f"Arquivo {request.file_name} não encontrado")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                return server_services_pb2.ExportToDatabaseResponse(success=False, message="Arquivo não encontrado")

            tree = etree.parse(file_path)
            root = tree.getroot()

            # Conectar ao PostgreSQL
            conn = pg8000.connect(
                user=DBUSERNAME,
                password=DBPASSWORD,
                host=DBHOST,
                port=DBPORT,
                database=DBNAME
            )
            cursor = conn.cursor()

            # Criar a tabela 'cities' se não existir
            create_table_query = """
            CREATE TABLE IF NOT EXISTS cities (
                id SERIAL PRIMARY KEY,
                branch VARCHAR(255),
                city VARCHAR(255),
                rating FLOAT,
                latitude FLOAT,
                longitude FLOAT
            );
            """
            cursor.execute(create_table_query)
            conn.commit()

            # Inserir os dados na BD
            for item in root.findall("Item"):
                branch = item.findtext("Branch")
                city = item.findtext("City")
                rating = float(item.findtext("Rating", "0"))
                latitude = float(item.findtext("Latitude", "0"))
                longitude = float(item.findtext("Longitude", "0"))

                cursor.execute("""
                    INSERT INTO cities (branch, city, rating, latitude, longitude)
                    VALUES (%s, %s, %s, %s, %s)
                """, (branch, city, rating, latitude, longitude))

            conn.commit()
            cursor.close()
            conn.close()

            return server_services_pb2.ExportToDatabaseResponse(success=True, message="Data exported successfully")

        except Exception as e:
            context.set_details(f"Error exporting the data {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.ExportToDatabaseResponse(success=False, message=f"Error exporting the data:{str(e)}")

    def SendFile(self, request, context):
        os.makedirs(MEDIA_PATH, exist_ok=True)
        file_path=os.path.join(MEDIA_PATH,request.file_name+ request.file_mime)

        file_in_bytes=request.file

        with open(file_path, 'wb') as f:
            f.write(file_in_bytes) 
            
        logger.info(f"{DBHOST}:{DBPORT}",exc_info=True)

        #Connect to database
        try:
            conn = pg8000.connect(user=f'{DBUSERNAME}', password=f'{DBPASSWORD}', host=f'{DBHOST}', port=f'{DBPORT}', database=f'{DBNAME}')
            cursor = conn.cursor()
            
            #Create Table
            create_table_query = f"CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR(100),email VARCHAR(100) UNIQUE NOT NULL,age INT)"
            cursor.execute(create_table_query)
            conn.commit()
            return server_services_pb2.SendFileResponseBody(success=True)
        except Exception as e:
            logger.error(f"Error connecting to database {DBHOST}:{DBPORT}",exc_info=True)
            context.set_details(f"Failed:{str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return server_services_pb2.SendFileResponseBody(success=False)

    def SendFileChunks(self, request_iterator, context):
        try:
            rabbit_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST,port=RABBITMQ_PORT,credentials=pika.PlainCredentials(RABBITMQ_USER,RABBITMQ_PW)))

            rabbit_channel = rabbit_connection.channel()
            rabbit_channel.queue_declare(queue='csv_chunks')

            os.makedirs(MEDIA_PATH, exist_ok=True)

            file_name = None
            file_chunks = [] #Store the chunks of the file

            for chunk in request_iterator:
                if not file_name:
                    file_name = chunk.file_name

                #Collect the file chunks   
                file_chunks.append(chunk.data)

                rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=chunk.data)
            
            rabbit_channel.basic_publish(exchange='', routing_key='csv_chunks', body=b'__EOF__')
        
            #Combine the chunks in a single file
            file_content = b"".join(file_chunks)

            file_path = os.path.join(MEDIA_PATH, file_name)
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
    
            return server_services_pb2.SendFileChunksResponse(success=True, message='Fileimported')

        except Exception as e:
            logger.error(f"Error: {str(e)}", exc_info=True)

            return server_services_pb2.SendFileChunksResponse(success=False, message='Error importing file')

def serve():
    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=MAX_WORKERS),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50 MB
        ]
    )
    add_SendFileServiceServicer_to_server(SendFileService(), server)
    server.add_insecure_port(f'[::]:{GRPC_SERVER_PORT}')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    print(f"Server running on port {GRPC_SERVER_PORT}")
    serve()