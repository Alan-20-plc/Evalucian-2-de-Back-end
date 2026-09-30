from django.urls import path
from . import views
from . import api_views
from rest_framework_simplejwt.views import TokenRefreshView
# Nuevas importaciones para Swagger
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # --- RUTAS WEB TRADICIONALES ---
    path('', views.catalogo_maquinarias, name='catalogo'),
    path('agregar/<int:maquinaria_id>/', views.agregar_al_carro, name='agregar_al_carro'),
    path('carro/', views.ver_carro, name='ver_carro'),
    path('generar-contrato/', views.generar_contrato, name='generar_contrato'),
    path('registro/', views.registro, name='registro'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    path('carro/eliminar/<int:item_id>/', views.eliminar_del_carro, name='eliminar_item'),
    path('maquinaria/<int:maquinaria_id>/', views.detalle_maquinaria, name='detalle_maquinaria'),
    # --- RUTAS DE LA API (DRF) ---
    path('api/catalogo/', api_views.api_catalogo, name='api_catalogo'),
    path('api/stock/<int:maquinaria_id>/', api_views.api_actualizar_stock, name='api_actualizar_stock'),
    
    # --- RUTAS DE AUTENTICACIÓN JWT ---
    path('api/login/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- RUTAS DE DOCUMENTACIÓN SWAGGER ---
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/carro-arriendo/', api_views.CarroClienteAPIView.as_view(), name='api_carro'),
    path('api/contratos/checkout/', api_views.CheckoutAPIView.as_view(), name='api_checkout'),
]