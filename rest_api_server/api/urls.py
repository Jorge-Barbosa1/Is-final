from django.urls import path
from .views.file_views import FileUploadView, FileUploadChunksView
from .views.users import GetAllUsers
from .views.process_csv import ProcessCsvView
from .views.filter_xml import filter_xml_by_xquery
from .views.validate_xml import ValidateXmlView 
from .views.export_to_db import export_xml_to_db

urlpatterns = [
    path('upload-file/', FileUploadView.as_view(), name='upload-file'),
    path('upload-file/by-chunks/', FileUploadChunksView.as_view(), name='upload-file-by-chunks'),
    path('users/', GetAllUsers.as_view(), name='users'),
    path('process-csv/', ProcessCsvView.as_view(), name='process-csv'),
    path('xml/filter-by/', filter_xml_by_xquery, name='filter-xml-by'),
    path('validate-xml/', ValidateXmlView.as_view(), name='validate-xml'),
    path('xml/export-to-db/', export_xml_to_db, name='export-xml-to-db'),
]
