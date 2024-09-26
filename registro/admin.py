from django.contrib import admin
from .models import Trabajador, Registro

@admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'apellido', 'cargo', 'vigente')

@admin.register(Registro)
class RegistroAdmin(admin.ModelAdmin):
    list_display = ('trabajador', 'fecha', 'hora_entrada', 'hora_salida', 'horas_trabajadas')