from django.db import models
from django.contrib.auth.models import User

"""
====================================================================
MODELOS DE CATÁLOGO E INVENTARIO
====================================================================
"""
class Categoria(models.Model):
    nombre = models.CharField(max_length=100)

    def __str__(self):
        return self.nombre

class Maquinaria(models.Model):
    nombre = models.CharField(max_length=150)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)
    tarifa_diaria = models.IntegerField(help_text="Costo por día de arriendo")
    garantia = models.IntegerField(help_text="Monto de garantía fija requerida")
    stock_disponible = models.IntegerField(help_text="Unidades físicas disponibles en flota")
    
    # Ahora sí está alineada con el resto de las propiedades
    imagen = models.ImageField(upload_to='maquinarias/', null=True, blank=True)

    def __str__(self):
        return f"{self.nombre} - Stock: {self.stock_disponible}"

"""
====================================================================
MODELOS DE CARRO DE COMPRAS PERSISTENTE (Requisito Evaluación)
====================================================================
"""
class CarroArriendo(models.Model):
    # Relación 1 a 1 entre el Usuario y su Carro activo
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Carro de {self.usuario.username}"

class ItemCarro(models.Model):
    carro = models.ForeignKey(CarroArriendo, related_name='items', on_delete=models.CASCADE)
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()

    def __str__(self):
        return f"{self.maquinaria.nombre} ({self.fecha_inicio} al {self.fecha_fin})"

"""
====================================================================
MODELOS DE TRANSACCIÓN Y ESTADOS (Uso de CHOICES obligatorio)
====================================================================
"""
class ContratoArriendo(models.Model):
    # Propiedad CHOICES exigida por la pauta
    ESTADOS_CONTRATO = [
        ('PENDIENTE', 'Pendiente de Pago'),
        ('PAGADO', 'Pagado - Stock Descontado'),
        ('ENTREGADO', 'Equipo Entregado al Cliente'),
        ('COMPLETADO', 'Equipo Devuelto - Stock Reincorporado'),
        ('CANCELADO', 'Cancelado - Stock Liberado'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADOS_CONTRATO, default='PENDIENTE')
    total_pagado = models.IntegerField(default=0)

    def __str__(self):
        return f"Contrato #{self.id} - {self.usuario.username} - {self.estado}"

class DetalleContrato(models.Model):
    contrato = models.ForeignKey(ContratoArriendo, related_name='detalles', on_delete=models.CASCADE)
    maquinaria = models.ForeignKey(Maquinaria, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    dias_arriendo = models.IntegerField()
    subtotal = models.IntegerField(help_text="Incluye tarifa por días + garantía")

    def __str__(self):
        return f"Detalle #{self.id} - {self.maquinaria.nombre}"