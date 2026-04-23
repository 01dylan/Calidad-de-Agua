from django.urls import path
from . import views

urlpatterns = [
    # Dashboard web
    path('',                    views.dashboard,           name='dashboard'),
    path('grafica',             views.grafica,             name='grafica'),

    # Devices
    path('api/devices',         views.get_devices,         name='get_devices'),

    # Readings
    path('api/readings',        views.get_readings,        name='get_readings'),
    path('api/readings/create', views.create_reading,      name='create_reading'),
    path('api/readings/latest', views.get_latest_reading,  name='latest_reading'),

    # Commands
    path('api/commands',        views.get_commands,        name='get_commands'),
    path('api/commands/create', views.create_command,      name='create_command'),
    path('api/commands/latest', views.get_latest_command,  name='latest_command'),

    # Alerts
    path('api/alerts',          views.get_alerts,          name='get_alerts'),

    # Thresholds
    path('api/thresholds',      views.get_threshold,       name='get_threshold'),

    # Logs
    path('api/logs/create',     views.create_log,          name='create_log'),
]