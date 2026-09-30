import os
import django
import requests
from django.core.files.base import ContentFile

# Configuramos el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nucleo.settings')
django.setup()

from aplicacion.models import Maquinaria

# Enlaces directos y ultra estables de maquinaria pesada
imagenes_estables = [
    "https://images.unsplash.com/photo-1579483070146-32d16d0061e8?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1541888946425-d0fbb18f724c?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1581094288338-2314dddb7ece?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80",
    "https://images.unsplash.com/photo-1578328819058-b69f3a3b0f6b?auto=format&fit=crop&w=800&q=80",
]

def forzar_descarga_fotos():
    maquinas = Maquinaria.objects.all()
    print("🚀 Forzando descarga de imágenes para todo el inventario...")
    
    for i, maquina in enumerate(maquinas):
        url = imagenes_estables[i % len(imagenes_estables)]
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                nombre = f"maquina_fix_{maquina.id}.jpg"
                maquina.imagen.save(nombre, ContentFile(res.content), save=True)
                print(f"✅ Foto lista para: {maquina.nombre}")
            else:
                print(f"⚠️ No se pudo con: {maquina.nombre}")
        except Exception as e:
            print(f"❌ Error en {maquina.nombre}: {e}")

    print("🎉 ¡Todas las fotos procesadas!")

if __name__ == '__main__':
    forzar_descarga_fotos()