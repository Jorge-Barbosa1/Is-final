import grpc
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from api.grpc.server_services_pb2 import XmlFilterRequest
from api.grpc.server_services_pb2_grpc import SendFileServiceStub
from rest_api_server.settings import GRPC_HOST, GRPC_PORT

@api_view(['POST'])
def filter_xml_by_xquery(request):
    try:

        file_name = request.data.get('file_name')
        xpath_query = request.data.get('xpath_query')


        if not file_name or not xpath_query:
            return Response(
                {"error": "file_name e xpath_query são obrigatórios"},
                status=status.HTTP_400_BAD_REQUEST
            )

        channel = grpc.insecure_channel(f"{GRPC_HOST}:{GRPC_PORT}")
        stub = SendFileServiceStub(channel)

        grpc_request = XmlFilterRequest(file_name=file_name, xpath_query=xpath_query)

        grpc_response = stub.FilterXml(grpc_request)

        results_list = list(grpc_response.results)

        return Response({
            "message": grpc_response.message,
            "results": results_list
        }, status=status.HTTP_200_OK)

    except grpc.RpcError as e:
        return Response(
            {"error": f"Erro no servidor gRPC: {e.details()}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
