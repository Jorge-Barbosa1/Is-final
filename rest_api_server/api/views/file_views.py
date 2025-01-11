from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from ..serializers.file_serializer import FileUploadSerializer
import os
#Adicionado
import grpc
import api.grpc.server_services_pb2 as server_services_pb2 
import api.grpc.server_services_pb2_grpc as server_services_pb2_grpc
from rest_api_server.settings import GRPC_PORT, GRPC_HOST

class FileUploadView(APIView):
    def post(self,request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "No file uploaded"}, status=400)
            
            file_name, file_extension = os.path.splitext(file.name)
            file_content = file.read()
            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.FileServiceStub(channel)

            grpc_request =  server_services_pb2.SendFileRequestBody( 
                file_name=file_name, 
                file_mime=file_extension, 
                file=file_content 
            )

            try:
                response = stub.SendFile(grpc_request)

                return Response({ 
                    "file_name": file_name, 
                    "file_extension": file_extension 
                }, status=status.HTTP_201_CREATED) 

            except grpc.RpcError as e: 
                return Response({"error": f"gRPC call failed: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class FileUploadChunksView(APIView):
    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "No file uploaded"}, status=400)

            channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
            stub = server_services_pb2_grpc.SendFileServiceStub(channel)

            # Função para gerar os chunks
            def generate_file_chunks(file, file_name, chunk_size=64*1024):
                try:
                    while chunk := file.read(chunk_size):
                        yield server_services_pb2.SendFileChunksRequest(
                            data=chunk,
                            file_name=file_name
                        )
                except Exception as e:
                    print(f"Error reading file: {e}")
                    raise 

            # Chamada gRPC para enviar os chunks
            try:
                response = stub.SendFileChunks(generate_file_chunks(file, file.name,(64*1024)))

                if response.success:
                    return Response({
                        "file_name": file.name,
                    }, status=status.HTTP_201_CREATED)

                return Response({
                    "error": response.message
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except grpc.RpcError as e:
                return Response({
                    "error": f"gRPC call failed: {e.details()}"
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)