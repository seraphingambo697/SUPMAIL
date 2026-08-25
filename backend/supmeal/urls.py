from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('accounts.urls')),
    path('api/', include('cookbooks.urls')),
    path('api/', include('recipes.urls')),
    path('api/', include('planning.urls')),
    path('api/', include('messaging.urls')),
    path('api/', include('importexport.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
