from django.urls import path
from . import views

urlpatterns = [
    path('crud/', views.crud, name='crud'),
    # Dashboard
    path('',                              views.dashboard,          name='dashboard'),
    path('grafica',                       views.grafica,            name='grafica'),

    # Devices CRUD
    path('api/devices',                   views.get_devices,        name='get_devices'),
    path('api/devices/create',            views.create_device,      name='create_device'),
    path('api/devices/<int:device_id>/update', views.update_device, name='update_device'),
    path('api/devices/<int:device_id>/delete', views.delete_device, name='delete_device'),

    # Readings CRUD
    path('api/readings',                  views.get_readings,       name='get_readings'),
    path('api/readings/latest',           views.get_latest_reading, name='latest_reading'),
    path('api/readings/create',           views.create_reading,     name='create_reading'),
    path('api/readings/<int:reading_id>/delete', views.delete_reading, name='delete_reading'),

    # Commands
    path('api/commands',                  views.get_commands,       name='get_commands'),
    path('api/commands/create',           views.create_command,     name='create_command'),
    path('api/commands/latest',           views.get_latest_command, name='latest_command'),

    # Alerts
    path('api/alerts',                    views.get_alerts,         name='get_alerts'),

    # Thresholds
    path('api/thresholds',                views.get_threshold,      name='get_threshold'),
    path('api/thresholds/<int:device_id>/update', views.update_threshold, name='update_threshold'),

    # Logs
    path('api/logs/create',               views.create_log,         name='create_log'),
]