import grpc
import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from api.grpc.server_services_pb2 import CsvToXmlRequest
from api.grpc.server_services_pb2_grpc import SendFileServiceStub
from rest_api_server.settings import GRPC_PORT, GRPC_HOST
from ..serializers.file_serializer import FileUploadSerializer


class ValidateXmlView(APIView):
    def post(self, request):
        # Validar o arquivo enviado
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            file = serializer.validated_data['file']

            if not file:
                return Response({"error": "Nenhum arquivo XML enviado"}, status=status.HTTP_400_BAD_REQUEST)

            file_name, file_extension = os.path.splitext(file.name)
            if file_extension != ".xml":
                return Response({"error": "Extensão de arquivo inválida. Por favor, envie um arquivo XML"}, status=status.HTTP_400_BAD_REQUEST)

            file_content = file.read()

            # Conectar ao servidor gRPC com limites ajustados
            channel = grpc.insecure_channel(
                f"{GRPC_HOST}:{GRPC_PORT}",
                options=[
                    ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MB
                    ('grpc.max_receive_message_length', 50 * 1024 * 1024)  # 50 MB
                ]
            )
            stub = SendFileServiceStub(channel)

            # Criar a requisição para o servidor gRPC
            request_grpc = CsvToXmlRequest(
                csv_file=file_content 
            )

            try:
                # Chamar o método no servidor gRPC
                response = stub.ValidateXml(request_grpc)

                # Retornar a resposta do servidor (XML validado ou mensagem de erro)
                if response.xml_content:
                    return Response({
                        "message": "XML validado com sucesso",
                        "xml_content": response.xml_content
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({"error": "Erro desconhecido ao validar o XML"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            except grpc.RpcError as e:
                # Retornar um erro caso a chamada gRPC falhe
                return Response({"error": f"Falha na chamada gRPC: {e.details()}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Caso a validação inicial falhe
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
