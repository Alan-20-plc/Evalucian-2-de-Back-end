from django.contrib import admin
from .models import Categoria, Maquinaria, CarroArriendo, ItemCarro, ContratoArriendo, DetalleContrato

# Registramos la categoría simple
admin.site.register(Categoria)

# Configuramos la vista de las máquinas para el profe
@admin.register(Maquinaria)
class MaquinariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'tarifa_diaria', 'stock_disponible')
    list_editable = ('stock_disponible',) # Permite al profe editar el stock directamente desde la lista
    search_fields = ('nombre',)

# Configuramos la vista de los contratos generados
@admin.register(ContratoArriendo)
class ContratoAdmin(admin.ModelAdmin):
    list_display = ('id', 'usuario', 'fecha_creacion', 'estado', 'total_pagado')
    list_filter = ('estado', 'fecha_creacion') # Filtros laterales
    list_editable = ('estado',) # Para que el profe pueda marcarlo como "ENTREGADO" o "DEVUELTO"

# Registramos los detalles secundarios
admin.site.register(DetalleContrato)
admin.site.register(CarroArriendo)
admin.site.register(ItemCarro)