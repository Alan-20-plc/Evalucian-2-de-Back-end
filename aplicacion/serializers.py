from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Categoria, Maquinaria, ContratoArriendo

class MaquinariaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Maquinaria
        fields = ['id', 'nombre', 'categoria_nombre', 'tarifa_diaria', 'garantia', 'stock_disponible']

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoArriendo
        fields = ['id', 'usuario', 'fecha_creacion', 'estado', 'total_pagado']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        # Agregamos el claim personalizado exigido por la rúbrica
        if user.is_staff:
            token['rol'] = 'Ejecutivo de Arriendos'
        else:
            token['rol'] = 'Empresa Constructora'
            
        token['username'] = user.username
        return token