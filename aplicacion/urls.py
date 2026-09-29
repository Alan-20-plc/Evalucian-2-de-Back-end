from django.urls import path
from . import views
from . import api_views  # <-- Importamos las vistas de la API

urlpatterns = [
    # Rutas web tradicionales que ya tenías
    path('', views.catalogo_maquinarias, name='catalogo'),
    path('agregar/<int:maquinaria_id>/', views.agregar_al_carro, name='agregar_al_carro'),
    path('carro/', views.ver_carro, name='ver_carro'),
    path('generar-contrato/', views.generar_contrato, name='generar_contrato'),
    path('registro/', views.registro, name='registro'),
    path('panel-admin/', views.panel_admin, name='panel_admin'),
    
    # --- NUEVAS RUTAS DE LA API (Requisito DRF) ---
    path('api/catalogo/', api_views.api_catalogo, name='api_catalogo'),
    path('api/stock/<int:maquinaria_id>/', api_views.api_actualizar_stock, name='api_actualizar_stock'),
]