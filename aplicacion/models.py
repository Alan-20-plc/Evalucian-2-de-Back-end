from django.db import models

class Programmer(models.Model):
    nombre = models.CharField(max_length=100)
    lenguaje_favorito = models.CharField(max_length=50)
    años_experiencia = models.IntegerField(default=0)

    def __str__(self):
        return self.nombre