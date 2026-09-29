from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
# Aquí en la línea 5 están agregados todos los modelos exactos de tu base de datos
from .models import Maquinaria, CarroArriendo, ItemCarro, ContratoArriendo, DetalleContrato

def catalogo_maquinarias(request):
    maquinarias = Maquinaria.objects.all().order_by('id')
    cantidad_carro = 0
    
    if request.user.is_authenticated:
        carro, created = CarroArriendo.objects.get_or_create(usuario=request.user)
        cantidad_carro = ItemCarro.objects.filter(carro=carro).count()
        
    return render(request, 'aplicacion/catalogo.html', {
        'maquinarias': maquinarias, 
        'cantidad_carro': cantidad_carro
    })

@login_required
def agregar_al_carro(request, maquinaria_id):
    maquinaria = get_object_or_404(Maquinaria, id=maquinaria_id)
    carro, created = CarroArriendo.objects.get_or_create(usuario=request.user)
    
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    
    ItemCarro.objects.get_or_create(
        carro=carro, 
        maquinaria=maquinaria,
        defaults={'fecha_inicio': hoy, 'fecha_fin': manana}
    )
        
    return redirect('catalogo')

@login_required
def ver_carro(request):
    carro, created = CarroArriendo.objects.get_or_create(usuario=request.user)
    items = ItemCarro.objects.filter(carro=carro)
    
    total_pagar = sum(item.maquinaria.tarifa_diaria for item in items)
    
    return render(request, 'aplicacion/carro.html', {'items': items, 'total_pagar': total_pagar})

# ESTA ES LA NUEVA FUNCIÓN QUE TOMA EL CARRO Y CREA EL CONTRATO OFICIAL
@login_required
def generar_contrato(request):
    # Solo aceptamos peticiones POST por seguridad (cuando se presiona el botón verde)
    if request.method == 'POST':
        carro = get_object_or_404(CarroArriendo, usuario=request.user)
        items = ItemCarro.objects.filter(carro=carro)
        
        if items.exists():
            # 1. Creamos el contrato en estado PENDIENTE con total 0 inicial
            contrato = ContratoArriendo.objects.create(
                usuario=request.user,
                estado='PENDIENTE',
                total_pagado=0
            )
            
            total_final = 0
            
            # 2. Procesamos cada máquina que estaba en el carro
            for item in items:
                # Calculamos los días de arriendo (mínimo 1 día)
                dias = (item.fecha_fin - item.fecha_inicio).days
                if dias < 1:
                    dias = 1
                
                # Subtotal exige sumar (tarifa * dias) + la garantía
                subtotal_item = (item.maquinaria.tarifa_diaria * dias) + item.maquinaria.garantia
                total_final += subtotal_item
                
                # Creamos el detalle histórico de esta máquina
                DetalleContrato.objects.create(
                    contrato=contrato,
                    maquinaria=item.maquinaria,
                    fecha_inicio=item.fecha_inicio,
                    fecha_fin=item.fecha_fin,
                    dias_arriendo=dias,
                    subtotal=subtotal_item
                )
                
                # 3. Descontamos 1 unidad del stock físico de la maquinaria
                item.maquinaria.stock_disponible -= 1
                item.maquinaria.save()
            
            # 4. Actualizamos el total a pagar en el contrato y guardamos
            contrato.total_pagado = total_final
            contrato.save()
            
            # 5. Vaciamos el carro de compras para que quede en cero
            items.delete()
            
    # Finalmente redirigimos de vuelta al inicio
    return redirect('catalogo')
# ---------------------------------------------------------
# NUEVAS VISTAS: REGISTRO Y PANEL ADMIN FRONTEND
# ---------------------------------------------------------

# 1. Vista para que nuevos clientes se registren
def registro(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Si se registra bien, lo mandamos a iniciar sesión
    else:
        form = UserCreationForm()
    return render(request, 'aplicacion/registro.html', {'form': form})

# 2. Vista del Panel de Administración en la app (Solo para el usuario 'allan' o admins)
def es_admin(user):
    return user.is_staff

@user_passes_test(es_admin)
def panel_admin(request):
    # Si el administrador envió el formulario para actualizar stock
    if request.method == 'POST' and 'actualizar_stock' in request.POST:
        maq_id = request.POST.get('maquinaria_id')
        nuevo_stock = request.POST.get('nuevo_stock')
        
        # Buscamos la máquina y le guardamos el nuevo número
        maquina = get_object_or_404(Maquinaria, id=maq_id)
        maquina.stock_disponible = int(nuevo_stock)
        maquina.save()
        
        return redirect('panel_admin') # Recargamos la página
        
    # Traemos todos los contratos y maquinarias
    contratos = ContratoArriendo.objects.all().order_by('-fecha_creacion')
    maquinarias = Maquinaria.objects.all().order_by('id')
    return render(request, 'aplicacion/panel_admin.html', {
        'contratos': contratos, 
        'maquinarias': maquinarias
    })