from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection

class GetAllUsers(APIView):
    def get(self, request):
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()

            users=[Book(id=row[0],name=row[1]) for row in users]
            return Response({"users": users}, status=status.HTTP_200_OK)
