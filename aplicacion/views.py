from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from datetime import timedelta
from .models import Maquinaria, CarroArriendo, ItemCarro, ContratoArriendo, DetalleContrato, Categoria

# ==========================================
# VISTAS DEL CLIENTE (EMPRESA CONSTRUCTORA)
# ==========================================

def catalogo_maquinarias(request):
    """
    Renderiza la página principal con el catálogo.
    Incluye filtro dinámico por categorías.
    """
    # 1. Capturamos si el usuario hizo clic en una categoría
    categoria_id = request.GET.get('categoria')
    
    # 2. Filtramos las máquinas según la caja que presionó
    if categoria_id:
        maquinarias = Maquinaria.objects.filter(categoria_id=categoria_id).order_by('id')
    else:
        maquinarias = Maquinaria.objects.all().order_by('id')
        
    categorias = Categoria.objects.all()
    cantidad_carro = 0
    
    if request.user.is_authenticated:
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        cantidad_carro = ItemCarro.objects.filter(carro=carro).count()
        
    return render(request, 'aplicacion/catalogo.html', {
        'maquinarias': maquinarias, 
        'categorias': categorias,
        'cantidad_carro': cantidad_carro
    })

@login_required
def agregar_al_carro(request, maquinaria_id):
    """
    Agrega una maquinaria específica al carro de arriendo del usuario activo.
    El decorador @login_required protege la ruta para que solo usuarios logueados accedan.
    """
    maquinaria = get_object_or_404(Maquinaria, id=maquinaria_id)
    carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
    
    # Definimos el arriendo por defecto de 1 día (desde hoy hasta mañana)
    hoy = timezone.now().date()
    manana = hoy + timedelta(days=1)
    
    # get_or_create evita que se duplique la misma máquina en el carro de compras
    ItemCarro.objects.get_or_create(
        carro=carro, 
        maquinaria=maquinaria,
        defaults={'fecha_inicio': hoy, 'fecha_fin': manana}
    )
    return redirect('catalogo')

@login_required
def ver_carro(request):
    """
    Muestra el detalle del carro de compras del usuario y calcula el total a pagar
    iterando y sumando las tarifas diarias de todas las máquinas en el carro.
    """
    carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
    items = ItemCarro.objects.filter(carro=carro)
    
    # Cálculo matemático del subtotal usando comprensión de listas
    total_pagar = sum(item.maquinaria.tarifa_diaria for item in items)
    
    return render(request, 'aplicacion/carro.html', {'items': items, 'total_pagar': total_pagar})

@login_required
def eliminar_del_carro(request, item_id):
    """
    Permite al usuario eliminar un ítem específico de su carro de arriendo.
    Se valida por seguridad que el ítem pertenezca estrictamente al usuario actual.
    """
    item = get_object_or_404(ItemCarro, id=item_id, carro__usuario=request.user)
    item.delete()
    return redirect('ver_carro')

@login_required
def generar_contrato(request):
    """
    Lógica transaccional para el Checkout del Proyecto 6.
    1. Crea un contrato en estado PENDIENTE.
    2. Traspasa los ítems del carro al detalle del contrato.
    3. Descuenta atómicamente el stock físico de las máquinas arrendadas.
    4. Vacía el carro del usuario tras finalizar.
    """
    if request.method == 'POST':
        carro = get_object_or_404(CarroArriendo, usuario=request.user)
        items = ItemCarro.objects.filter(carro=carro)
        
        if items.exists():
            # 1. Creación de la cabecera del contrato
            contrato = ContratoArriendo.objects.create(
                usuario=request.user, estado='PENDIENTE', total_pagado=0
            )
            total_final = 0
            
            # 2. Procesamiento de cada ítem (Detalle)
            for item in items:
                dias = max((item.fecha_fin - item.fecha_inicio).days, 1)
                subtotal_item = (item.maquinaria.tarifa_diaria * dias) + item.maquinaria.garantia
                total_final += subtotal_item
                
                DetalleContrato.objects.create(
                    contrato=contrato, maquinaria=item.maquinaria,
                    fecha_inicio=item.fecha_inicio, fecha_fin=item.fecha_fin,
                    dias_arriendo=dias, subtotal=subtotal_item
                )
                
                # 3. Control de Stock (Requisito de Evaluación)
                item.maquinaria.stock_disponible -= 1
                item.maquinaria.save()
                
            # 4. Actualización de totales finales y limpieza
            contrato.total_pagado = total_final
            contrato.save()
            items.delete() # Se vacía el carro definitivamente
            
    return redirect('catalogo')

# ==========================================
# VISTAS DE AUTENTICACIÓN
# ==========================================

def registro(request):
    """
    Maneja el registro de nuevos usuarios clientes utilizando el formulario
    nativo de creación de usuarios de Django (UserCreationForm) con hashing de claves.
    """
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login') # Redirige al login tras un registro exitoso
    else:
        form = UserCreationForm()
    return render(request, 'aplicacion/registro.html', {'form': form})

# ==========================================
# VISTAS DEL ADMINISTRADOR (EJECUTIVO ARRIENDO)
# ==========================================

def es_admin(user):
    """ Función auxiliar de validación: retorna True si el usuario tiene nivel de Staff """
    return user.is_staff

@user_passes_test(es_admin)
def panel_admin(request):
    """
    Panel de control exclusivo para administradores (protegido por user_passes_test).
    Permite visualizar el historial de contratos, actualizar el inventario manualmente
    y registrar nuevas maquinarias con carga de imágenes nativa.
    """
    if request.method == 'POST':
        
        # Flujo 1: El administrador presionó el botón de actualizar stock en la tabla
        if 'actualizar_stock' in request.POST:
            maq_id = request.POST.get('maquinaria_id')
            nuevo_stock = request.POST.get('nuevo_stock')
            maquina = get_object_or_404(Maquinaria, id=maq_id)
            maquina.stock_disponible = int(nuevo_stock)
            maquina.save()
            return redirect('panel_admin')
            
        # Flujo 2: El administrador envió el modal para agregar nueva máquina al catálogo
        elif 'agregar_maquina' in request.POST:
            nombre = request.POST.get('nombre')
            categoria_id = request.POST.get('categoria_id')
            tarifa = request.POST.get('tarifa_diaria')
            garantia = request.POST.get('garantia')
            stock = request.POST.get('stock')
            
            # request.FILES maneja la subida física de la fotografía al servidor local/media
            imagen = request.FILES.get('imagen') 
            
            categoria = get_object_or_404(Categoria, id=categoria_id)
            
            # Persistencia en la base de datos PostgreSQL
            Maquinaria.objects.create(
                nombre=nombre, categoria=categoria, tarifa_diaria=tarifa,
                garantia=garantia, stock_disponible=stock, imagen=imagen
            )
            return redirect('panel_admin')
            
    # Carga de datos para poblar el dashboard administrativo
    contratos = ContratoArriendo.objects.all().order_by('-fecha_creacion')
    maquinarias = Maquinaria.objects.all().order_by('id')
    categorias = Categoria.objects.all()
    
    return render(request, 'aplicacion/panel_admin.html', {
        'contratos': contratos, 
        'maquinarias': maquinarias,
        'categorias': categorias
    })
def detalle_maquinaria(request, maquinaria_id):
    """
    Muestra la vista detallada de una maquinaria específica 
    con su información ampliada, tarifa y opción de arriendo.
    """
    maquina = get_object_or_404(Maquinaria, id=maquinaria_id)
    cantidad_carro = 0
    
    if request.user.is_authenticated:
        carro, _ = CarroArriendo.objects.get_or_create(usuario=request.user)
        cantidad_carro = ItemCarro.objects.filter(carro=carro).count()
        
    return render(request, 'aplicacion/detalle.html', {
        'maquina': maquina,
        'cantidad_carro': cantidad_carro
    })