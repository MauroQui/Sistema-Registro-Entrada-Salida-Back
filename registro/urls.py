from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TrabajadorViewSet, RegistroViewSet, login_view, liquidacion_trabajador
from . import views

# Se crea una instancia de DefaultRouter
router = DefaultRouter()

# Registro de viewsets
router.register(r'trabajadores', TrabajadorViewSet)
router.register(r'registros', RegistroViewSet)

urlpatterns = [
    
    #Ruta para la Api Rest
    path('api/', include(router.urls)), 
    
     # Ruta para el login de la API
    path('api/login/', login_view, name='login'),
    
    #Ruta para vistas de las clases
    path('trabajadores/', views.TrabajadorListView.as_view(), name='trabajadores'),
    path('trabajador/<int:pk>/', views.TrabajadorDetailView.as_view(), name='trabajador_detalle'),
    path('registros/', views.RegistroListView.as_view(), name='registros'),
    path('registro/<int:pk>/', views.RegistroDetailView.as_view(), name='registro_detalle'),
    
    #Ruta para simulador NFC con datos estaticos
    path('nfc_simulator_static/', views.nfc_simulator_static, name='nfc_simulator_static'),
    
    # Ruta para la liquidación
    path('api/trabajadores/<int:id>/liquidacion/', liquidacion_trabajador, name='liquidacion-trabajador'), 
    # path('liquidacion/', views.calcular_liquidacion, name='calcular_liquidacion'),
    path('api/liquidacion-trabajador/<int:id>/', views.liquidacion_trabajador, name='liquidacion-trabajador'),
    
    #Ruta para llegadas tardias
    path('api/trabajadores/reportes/llegadas-tardias/', views.exportar_llegadas_tardias_csv, name='exportar_llegadas_tardias'),
    #Ruta para llegadas tempranas
    path('api/trabajadores/reportes/llegadas-tempranas/', views.exportar_llegadas_tempranas_csv, name='exportar_llegadas_tempranas'),
    #Ruta para salidas tardias
    path('api/trabajadores/reportes/salidas-tardias/', views.exportar_salidas_tardias_csv, name='exportar_salidas_tardias'),
    #Ruta para salidas tempranas
     path('api/trabajadores/reportes/salidas-tempranas/', views.exportar_salidas_tempranas_csv, name='exportar_salidas_tempranas'),
    #Ruta para ausencias
    path('api/trabajadores/reportes/ausencias/', views.exportar_ausencias_csv, name='exportar_ausencias'),
]

