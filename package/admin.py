from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export import resources
from .models import *
# Register your models here.

admin.site.register(Package)
admin.site.register(User_Package)