from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import timedelta

from .models import Maquinaria, CarroArriendo, ItemCarro, ContratoArriendo, DetalleContrato
from .serializers import MaquinariaSerializer, ContratoSerializer, CustomTokenObtainPairSerializer

# --- AUTENTICACIÓN JWT ---

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# --- ENDPOINTS BÁSICOS ---

@api_view(['GET'])
@permission_classes([AllowAny])
def api_catalogo(request):
    maquinarias = Maquinaria.objects.all().order_by('id')
    serializer = MaquinariaSerializer(maquinarias, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def api_actualizar_stock(request, maquinaria_id):
    try:
        maquina = Maquinaria.objects.get(id=maquinaria_id)
    except Maquinaria.DoesNotExist:
        return Response({'error': 'Máquina no encontrada'}, status=404)
    
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


# --- ENDPOINTS DEL ADMINISTRADOR (INVENTARIO) ---

class MaquinariaAPIView(generics.ListCreateAPIView):
    """ GET: Público | POST: Solo Administrador """
    queryset = Maquinaria.objects.all()
    serializer_class = MaquinariaSerializer
    filterset_fields = ['categoria', 'tarifa_diaria']

    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdminUser()]

class MaquinariaDetalleAPIView(generics.RetrieveUpdateDestroyAPIView):
    """ PUT / PATCH / DELETE: Solo Administrador """
    queryset = Maquinaria.objects.all()
    serializer_class = MaquinariaSerializer
    permission_classes = [IsAdminUser]


# --- ENDPOINTS DEL CLIENTE (EMPRESA CONSTRUCTORA) ---

class CarroClienteAPIView(APIView):
    """ GET: Ver carro | POST: Agregar máquina | DELETE: Vaciar carro """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        items = ItemCarro.objects.filter(carro=carro)
        data = [
            {"item_id": i.id, "maquinaria": i.maquinaria.nombre, "tarifa": i.maquinaria.tarifa_diaria} 
            for i in items
        ]
        return Response({"carro_usuario": request.user.username, "items": data})

    def post(self, request):
        maquinaria_id = request.data.get('maquinaria_id')
        try:
            maquinaria = Maquinaria.objects.get(id=maquinaria_id)
            carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
            
            ItemCarro.objects.create(
                carro=carro, 
                maquinaria=maquinaria,
                fecha_inicio=timezone.now().date(),
                fecha_fin=timezone.now().date() + timedelta(days=1)
            )
            return Response({"mensaje": f"{maquinaria.nombre} agregada al carro API"}, status=status.HTTP_201_CREATED)
        except Maquinaria.DoesNotExist:
            return Response({"error": "Máquina no encontrada"}, status=status.HTTP_404_NOT_FOUND)

class CheckoutAPIView(APIView):
    """ POST: Pagar y generar el contrato validando stock """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        carro = get_object_or_404(CarroArriendo, usuario=request.user)
        items = ItemCarro.objects.filter(carro=carro)
        
        if not items.exists():
            return Response({"error": "El carro está vacío"}, status=status.HTTP_400_BAD_REQUEST)

        contrato = ContratoArriendo.objects.create(
            usuario=request.user, estado='PAGADO', total_pagado=0
        )
        
        total_final = 0
        for item in items:
            if item.maquinaria.stock_disponible < 1:
                contrato.delete()
                return Response({"error": f"Sin stock para {item.maquinaria.nombre}. Transacción rechazada."}, status=status.HTTP_400_BAD_REQUEST)

            dias = max((item.fecha_fin - item.fecha_inicio).days, 1)
            subtotal = (item.maquinaria.tarifa_diaria * dias) + item.maquinaria.garantia
            total_final += subtotal
            
            DetalleContrato.objects.create(
                contrato=contrato, maquinaria=item.maquinaria,
                fecha_inicio=item.fecha_inicio, fecha_fin=item.fecha_fin,
                dias_arriendo=dias, subtotal=subtotal
            )
            
            item.maquinaria.stock_disponible -= 1
            item.maquinaria.save()

        contrato.total_pagado = total_final
        contrato.save()
        items.delete()
        
        return Response({"mensaje": "Contrato pagado exitosamente", "contrato_id": contrato.id, "total": total_final})