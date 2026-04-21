from django.urls import path
from . import views

urlpatterns = [
    path('devices', views.get_devices),

    path('readings', views.get_readings),
    path('readings/create', views.create_reading),

    path('commands', views.get_commands),
    path('commands/create', views.create_command),
    path('commands/latest', views.get_latest_command),
    path('grafica', views.grafica),
]