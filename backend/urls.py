from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.contrib.staticfiles.urls import static
from bulkImport.views import BulkImportView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('authentication.urls')),
    path('api/exam/', include('exam.urls')),
    path('api/package/', include('package.urls')),
    path('api/userinfo/', include('userInfo.urls')),
    path('api/img/', include('img.urls')),
    path('api/banner/', include('banner.urls')),
    path('api/designcontest/', include('designcontest.urls')),
    path('api/newsFeed/', include('newsFeed.urls')),
    path('api/notification/', include('notification.urls')),
    path('auth/', include('dj_rest_auth.urls')),
    path(r"accounts/", include("allauth.urls")),
    path('import', BulkImportView.as_view())
]

if settings.DEBUG:
        urlpatterns += static(settings.MEDIA_URL,
                              document_root=settings.MEDIA_ROOT)