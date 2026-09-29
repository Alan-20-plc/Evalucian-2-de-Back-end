from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Esta es la línea clave que habilita las rutas 'login' y 'logout'
    path('accounts/', include('django.contrib.auth.urls')), 
    
    path('', include('aplicacion.urls')),
]

# Habilita la visualización de imágenes que configuramos antes
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)