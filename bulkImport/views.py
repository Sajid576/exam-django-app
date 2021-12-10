import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions, exceptions
from django.contrib.auth.models import User, Group

from .uploadData import BulkImport
from customized_response.constants import *
from customized_response.response import *


class IsAdminOrDataEntryOperator(permissions.BasePermission): 
    def has_permission(self, request, view):
        user = request.user
        super_user = user and user.is_superuser
        if super_user or user.groups.filter(name='DataEntryOperator').exists():
            return True
        resp = error_resp(PERMISSION_DENIED, 'PERMISSION_DENIED')
        raise exceptions.NotAuthenticated(resp)


class BulkImportView(APIView):
    permission_classes = (IsAdminOrDataEntryOperator,)
    
    def post(self, request, *args, **kwargs):
        sheetName = request.POST.get('primarySheetName')
        # body_unicode = request.body.decode('cp1252')
        # body = json.loads(body_unicode)
        # sheetName = body['primarySheetName']
        dataFile = request.FILES['dataFile']
        if dataFile.name.endswith('.xlsx'):
            resp, ret_val = BulkImport.bulkImport(dataFile, sheetName)
            if ret_val == -1:
                resp = error_resp(WRONG_SHEET_NAME, 'WRONG_SHEET_NAME')
                return Response(resp, CODE400)
            
            elif ret_val == 1:
                if resp.get('error') == 'NULL': 
                    return Response(resp, CODE200)
                else:
                    return Response(resp, CODE400)
            else:
                resp = error_resp(WRONG_DATA_FORMAT, 'WRONG_DATA_FORMAT', resp)
                return Response(resp, CODE400)
        else:
            resp = error_resp(WRONG_FILE_EXT, 'WRONG_FILE_EXT')
            return Response(resp, CODE400)