from django.contrib import admin

from .models import *

class ContestDataAdmin(admin.ModelAdmin):
    readonly_fields = ('submitTime', )

# Register your models here.
admin.site.register(DesignContest)
admin.site.register(ContestData, ContestDataAdmin)
admin.site.register(ContestImage)

#admin.site.register(ContestEnroll)