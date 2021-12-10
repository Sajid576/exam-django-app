from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *

class ContestNewsAdmin(admin.ModelAdmin):
    readonly_fields = ('winnerAnnounceTime', )

# Register your models here.
admin.site.register(NewsFeed)
admin.site.register(NewsFeedImage)
admin.site.register(ContestNews, ContestNewsAdmin)
