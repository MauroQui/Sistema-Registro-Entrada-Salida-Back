from rest_framework import serializers
from .models import Registro, Trabajador

class TrabajadorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trabajador
        fields = ['id', 'nombre', 'apellido', 'cargo']

class RegistroSerializer(serializers.ModelSerializer):
    trabajador = TrabajadorSerializer(read_only=True)  # Incluir datos completos del trabajador

    class Meta:
        model = Registro
        fields = ['id', 'fecha', 'hora_entrada', 'hora_salida', 'trabajador']