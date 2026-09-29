from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import Maquinaria, ContratoArriendo
from .serializers import MaquinariaSerializer, ContratoSerializer

# 1. Endpoint Público para lectura de catálogo (Cualquiera puede verlo)
@api_view(['GET'])
@permission_classes([AllowAny])
def api_catalogo(request):
    maquinarias = Maquinaria.objects.all().order_by('id')
    serializer = MaquinariaSerializer(maquinarias, many=True)
    return Response(serializer.data)

# 2. Endpoint Restringido para gestión de inventario (SOLO Administradores)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def api_actualizar_stock(request, maquinaria_id):
    try:
        maquina = Maquinaria.objects.get(id=maquinaria_id)
    except Maquinaria.DoesNotExist:
        return Response({'error': 'Máquina no encontrada'}, status=404)
    
    # Recibimos el nuevo stock en formato JSON
    nuevo_stock = request.data.get('stock_disponible')
    
    if nuevo_stock is not None:
        maquina.stock_disponible = int(nuevo_stock)
        maquina.save()
        return Response({
            'mensaje': 'Stock actualizado correctamente', 
            'maquina': maquina.nombre,
            'nuevo_stock': maquina.stock_disponible
        })
        
    return Response({'error': 'Debes enviar el campo stock_disponible'}, status=400)