from django.contrib import admin
from .models import *

class NotificationUserAdmin(admin.ModelAdmin):
    readonly_fields = ('sendTime', )

admin.site.register(Notification)
admin.site.register(NotificationUser, NotificationUserAdmin)