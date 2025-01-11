import grpc
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.grpc.server_services_pb2 import CsvToXmlRequest
from api.grpc.server_services_pb2_grpc import SendFileServiceStub
from rest_api_server.settings import GRPC_PORT, GRPC_HOST
from ..serializers.file_serializer import FileUploadSerializer

class ProcessCsvView(APIView):
    def post(self, request):
        #validate the file 
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "No CSV file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

            file_name, file_extension = os.path.splitext(file.name)
            if file_extension != ".csv":
                return Response({"error": "Invalid file extension. Please upload a CSV file"}, status=status.HTTP_400_BAD_REQUEST)

            file_content = file.read()

            #Connect to gRPC server
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = SendFileServiceStub(channel)

            #Create request to grpc
            request = CsvToXmlRequest(
                csv_file=file_content,
                schema_path=""
            )

            try:
                #Call the method in the gRPC server
                response = stub.ProcessCsvToXml(request)

                #Return the XML gerated
                return Response({
                    "xml_content": response.xml_content
                }, status=status.HTTP_201_CREATED)
            
            except grpc.RpcError as e:
                return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)