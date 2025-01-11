import grpc
from . import server_services_pb2
from . import server_services_pb2_grpc

def convert_csv_to_xml(file_path, schema_path=None):
    with open(file_path, "rb") as f:
        csv_file = f.read()

    with grpc.insecure_channel("grpc-server:50051") as channel:
        stub = server_services_pb2_grpc.SendFileServiceStub(channel)
        response = stub.ProcessCsvToXml(server_services_pb2.CsvToXmlRequest(
            csv_file=csv_file,
            schema_path=schema_path or ""
        ))
        return response.xml_content
