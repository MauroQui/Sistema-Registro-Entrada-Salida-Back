from django.db import models
from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import now

class Trabajador(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)
    vigente = models.BooleanField(default=True)  # True para vigente, False para no vigente

    def __str__(self):
        return f"{self.nombre} {self.apellido}"
    
    # Método para calcular el total de horas trabajadas en un mes específico
    def total_horas_mes(self, mes, año):
        registros_mes = Registro.objects.filter(trabajador=self, fecha__year=año, fecha__month=mes)
        total_horas = sum([registro.horas_trabajadas() for registro in registros_mes])
        return total_horas
    # Método para calcular la liquidación de un trabajador para un mes y año específicos
    def calcular_liquidacion(self, mes, año, tarifa_hora):
        total_horas = self.total_horas_mes(mes, año)
        liquidacion = total_horas * tarifa_hora
        return liquidacion

class Registro(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now) 
    hora_entrada = models.TimeField()
    hora_salida = models.TimeField(null=True, blank=True)

    # Método para calcular las horas trabajadas en un día
    def horas_trabajadas(self):
        if self.hora_salida:
            hrsTotalDia = datetime.combine(self.fecha, self.hora_salida) - datetime.combine(self.fecha, self.hora_entrada)
            return round(hrsTotalDia.total_seconds() / 3600, 3) 
        return 0
    
    # Validaciones al guardar un registro
    def save(self, *args, **kwargs):
        # Aqui se valida si ya hay un registro de entrada para el día sin hora de salida
        if self.hora_entrada and not self.hora_salida:
            if Registro.objects.filter(trabajador=self.trabajador, fecha=self.fecha, hora_salida__isnull=True).exists():
                raise ValueError("Ya existe un registro de entrada para hoy sin hora de salida.")

        # Aqui se valida si ya hay un registro de salida para el día
        if self.hora_salida:
            if Registro.objects.filter(trabajador=self.trabajador, fecha=self.fecha, hora_salida__isnull=False).exists():
                raise ValueError("Ya se ha registrado la salida para hoy.")

        super(Registro, self).save(*args, **kwargs)

    def __str__(self):
        return f"Registro de {self.trabajador} el {self.fecha}"
