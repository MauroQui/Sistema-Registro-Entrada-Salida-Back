from rest_framework import viewsets
from django.views.generic import ListView, DetailView
from .models import Trabajador, Registro
from .serializers import TrabajadorSerializer, RegistroSerializer
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.utils.timezone import now
import datetime
import csv
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


# Listas y detalles de trabajadores
class TrabajadorListView(ListView):
    model = Trabajador
    template_name = 'registro/trabajador_list.html'
    context_object_name = 'trabajadores'

class TrabajadorDetailView(DetailView):
    model = Trabajador
    template_name = 'registro/trabajador_detail.html'
    context_object_name = 'trabajador'

# API ViewSets para Trabajador y Registro    
class TrabajadorViewSet(viewsets.ModelViewSet):
    queryset = Trabajador.objects.all()
    serializer_class = TrabajadorSerializer

class RegistroViewSet(viewsets.ModelViewSet):
    queryset = Registro.objects.all()
    serializer_class = RegistroSerializer

class RegistroListView(ListView):
    model = Registro
    template_name = 'registro/registro_list.html'
    context_object_name = 'registros'

class RegistroDetailView(DetailView):
    model = Registro
    template_name = 'registro/registro_detail.html'
    context_object_name = 'registro'
    
# Página principal    
def home(request):
    return render(request, 'home.html')

# Simulador NFC con datos estáticos
def nfc_simulator_static(request):
    trabajador = Trabajador.objects.first()  

    if trabajador:
        # Verificar si ya existe un registro sin hora de salida para hoy
        registro_existente = Registro.objects.filter(trabajador=trabajador, fecha=now().date(), hora_salida__isnull=True).exists()
        
         # Crear un registro de entrada si no existe un registro incompleto para hoy
        if not registro_existente:
            registro = Registro(trabajador=trabajador, fecha=now().date(), hora_entrada=now().time())
            registro.save()

    return HttpResponse("Simulación de NFC con datos estáticos realizada.")

# Calcular la liquidación mensual de todos los trabajadores
def calcular_liquidacion(request):
    trabajadores = Trabajador.objects.filter(vigente=True)
    liquidaciones = []

    for trabajador in trabajadores:
        # Llama al método calcular_liquidacion de Trabajador
        liquidacion = trabajador.calcular_liquidacion(now().month, now().year, tarifa_hora=5.416)

        # Agregar la liquidación a la lista
        liquidaciones.append({
            'trabajador': trabajador,
            'liquidacion': liquidacion,
        })

    return render(request, 'registro/liquidacion.html', {'liquidaciones': liquidaciones})

#Calcular liquidacion trabajador
def liquidacion_trabajador(request, id):
    try:
        # Obtener el trabajador por su ID, o lanzar un 404 si no se encuentra
        trabajador = get_object_or_404(Trabajador, pk=id)
        mes_actual = now().month
        año_actual = now().year
        tarifa_hora = 5.416  # Puedes modificar esto si es necesario

        # Calcular la liquidación usando el método en tu modelo Trabajador
        liquidacion = trabajador.calcular_liquidacion(mes_actual, año_actual, tarifa_hora)
        total_horas = trabajador.total_horas_mes(mes_actual, año_actual)

        # Crear el diccionario con los datos que necesitas devolver
        data = {
            'trabajador': {
                'nombre': trabajador.nombre,
                'apellido': trabajador.apellido,
                'cargo': trabajador.cargo,
            },
            'total_horas': total_horas,
            'liquidacion': liquidacion,
        }

        # Enviar los datos como JSON
        return JsonResponse(data)

    except Exception as e:
        # Imprimir el error en la consola y devolver una respuesta JSON con el mensaje de error
        print(f"Error al calcular la liquidación del trabajador {id}: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
    
# Exportar llegadas tardías en CSV
def exportar_llegadas_tardias_csv(request):
    # Definir la hora límite de llegada
    hora_limite = datetime.time(8, 5)  # 8:00 AM

    # Filtrar los registros que tienen horas de entrada después de la hora límite
    registros_llegadas_tardias = Registro.objects.filter(hora_entrada__gt=hora_limite)

    # Crear el HttpResponse con el tipo de contenido 'text/csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_llegadas_tardias.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)
    
    # Escribir la fila de cabeceras
    writer.writerow(['Trabajador', 'Fecha', 'Hora de Entrada', 'Hora de Salida'])

    # Escribir los datos de los registros
    if registros_llegadas_tardias.exists():
        for registro in registros_llegadas_tardias:
            writer.writerow([
                registro.trabajador.nombre,  # Puedes ajustar cómo mostrar el nombre del trabajador
                registro.fecha.strftime('%Y-%m-%d'),
                registro.hora_entrada.strftime('%H:%M'),
                registro.hora_salida.strftime('%H:%M') if registro.hora_salida else 'No registrada'
            ])
    else:
        writer.writerow(['No hay llegadas tardías registradas.'])

    return response

#Exportar llegadas tempranas en CSV
def exportar_llegadas_tempranas_csv(request):
    
    # Definir la hora límite de llegada
    hora_limite = datetime.time(8, 0)  # 8:00 AM

    # Filtrar los registros que tienen horas de entrada antes de la hora límite
    registros_llegadas_tempranas = Registro.objects.filter(hora_entrada__lt=hora_limite)

    # Crear el HttpResponse con el tipo de contenido 'text/csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_llegadas_tempranas.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)
    # Escribir la fila de cabeceras
    writer.writerow(['Trabajador', 'Fecha', 'Hora de Entrada', 'Hora de Salida'])

    # Escribir los datos de los registros
    if registros_llegadas_tempranas.exists():
        for registro in registros_llegadas_tempranas:
            writer.writerow([
                registro.trabajador.nombre,
                registro.fecha.strftime('%Y-%m-%d'),
                registro.hora_entrada.strftime('%H:%M'),
                registro.hora_salida.strftime('%H:%M') if registro.hora_salida else 'No registrada'
            ])
    else:
        writer.writerow(['No hay llegadas tempranas registradas.'])

    return response

#Exportar salidas tardias en CSV
def exportar_salidas_tardias_csv(request):
    # Definir la hora límite de salida
    hora_limite = datetime.time(17, 0)  # 5:00 PM

    # Filtrar los registros que tienen horas de salida después de la hora límite
    registros_salidas_tardias = Registro.objects.filter(hora_salida__gt=hora_limite)

    # Crear el HttpResponse con el tipo de contenido 'text/csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_salidas_tardias.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)
   
    # Escribir la fila de cabeceras
    writer.writerow(['Trabajador', 'Fecha', 'Hora de Entrada', 'Hora de Salida'])

    # Escribir los datos de los registros
    if registros_salidas_tardias.exists():
        for registro in registros_salidas_tardias:
            writer.writerow([
                registro.trabajador.nombre,
                registro.fecha.strftime('%Y-%m-%d'),
                registro.hora_entrada.strftime('%H:%M'),
                registro.hora_salida.strftime('%H:%M')
            ])
    else:
        writer.writerow(['No hay salidas tardías registradas.'])

    return response

#Exportar salidas tempranas en CSV
def exportar_salidas_tempranas_csv(request):
    # Definir la hora límite de salida
    hora_limite = datetime.time(17, 0)  # 5:00 PM

    # Filtrar los registros que tienen horas de salida antes de la hora límite
    registros_salidas_tempranas = Registro.objects.filter(hora_salida__lt=hora_limite)

    # Crear el HttpResponse con el tipo de contenido 'text/csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_salidas_tempranas.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)
    # Escribir la fila de cabeceras
    writer.writerow(['Trabajador', 'Fecha', 'Hora de Entrada', 'Hora de Salida'])

    # Escribir los datos de los registros
    if registros_salidas_tempranas.exists():
        for registro in registros_salidas_tempranas:
            writer.writerow([
                registro.trabajador.nombre,
                registro.fecha.strftime('%Y-%m-%d'),
                registro.hora_entrada.strftime('%H:%M'),
                registro.hora_salida.strftime('%H:%M')
            ])
    else:
        writer.writerow(['No hay salidas tempranas registradas.'])

    return response


#Exportar ausencias en CSV
def exportar_ausencias_csv(request):
    fecha_inicio = now().date() - datetime.timedelta(days=30) 
    fecha_fin = now().date() 

    # Obtener todos los trabajadores
    trabajadores = Trabajador.objects.all()

    # Obtener todas las fechas en el rango especificado
    fechas = [fecha_inicio + datetime.timedelta(days=x) for x in range((fecha_fin - fecha_inicio).days + 1)]

    # Crear el HttpResponse con el tipo de contenido 'text/csv'
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reporte_ausencias.csv"'

    # Crear el escritor CSV
    writer = csv.writer(response)
    # Escribir la fila de cabeceras
    writer.writerow(['Trabajador', 'Fecha'])

    # Verificar ausencias
    for trabajador in trabajadores:
        for fecha in fechas:
            if not Registro.objects.filter(trabajador=trabajador, fecha=fecha).exists():
                writer.writerow([trabajador, fecha])

    return response

#Vista para el Login desde el Frontend
@api_view(['POST'])
def login_view(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is not None:
       
        return Response({'message': 'Login exitoso'}, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Credenciales inválidas'}, status=status.HTTP_400_BAD_REQUEST)



