from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import grpc
from api.grpc.server_services_pb2 import ExportToDatabaseRequest
from api.grpc.server_services_pb2_grpc import SendFileServiceStub
from rest_api_server.settings import GRPC_HOST, GRPC_PORT

@api_view(['POST'])
def export_xml_to_db(request):
    try:
        # Receber os parâmetros
        file_name = request.data.get('file_name')

        # Validar o parâmetro
        if not file_name:
            return Response(
                {"error": "file_name is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Conectar ao servidor gRPC
        channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        stub = SendFileServiceStub(channel)

        grpc_request = ExportToDatabaseRequest(file_name=file_name)
        grpc_response = stub.ExportToDatabase(grpc_request)

        if grpc_response.success:
            return Response({
                "message": grpc_response.message
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": grpc_response.message
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    except grpc.RpcError as e:
        return Response(
            {"error": f"Error on gRPC server: {e.details()}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
