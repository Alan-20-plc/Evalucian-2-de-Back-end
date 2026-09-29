from rest_framework import serializers
from .models import Categoria, Maquinaria, ContratoArriendo

class MaquinariaSerializer(serializers.ModelSerializer):
    categoria_nombre = serializers.ReadOnlyField(source='categoria.nombre')

    class Meta:
        model = Maquinaria
        # Elegimos qué datos se van a enviar por la API
        fields = ['id', 'nombre', 'categoria_nombre', 'tarifa_diaria', 'garantia', 'stock_disponible']

class ContratoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContratoArriendo
        fields = ['id', 'usuario', 'fecha_creacion', 'estado', 'total_pagado']