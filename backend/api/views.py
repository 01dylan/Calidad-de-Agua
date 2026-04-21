from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import *
import json
from django.shortcuts import render


# DEVICES

def get_devices(request):
    data = list(Device.objects.values())
    return JsonResponse(data, safe=False)


# READINGS

@csrf_exempt
def create_reading(request):
    if request.method == "POST":
        data = json.loads(request.body)

        reading = Reading.objects.create(
            device_id=data["device_id"],
            temperatura=data["temperatura"],
            turbidez=data["turbidez"],
            conductividad=data["conductividad"],
            ph=data["ph"],
            estado=data["estado"]
        )

        return JsonResponse({"ok": True})

def get_readings(request):
    data = list(Reading.objects.values())
    return JsonResponse(data, safe=False)


# COMMANDS

@csrf_exempt
def create_command(request):
    if request.method == "POST":
        data = json.loads(request.body)

        command = Command.objects.create(
            device_id=data["device_id"],
            command=data["command"]
        )

        return JsonResponse({"ok": True})

def get_commands(request):
    data = list(Command.objects.values())
    return JsonResponse(data, safe=False)

def get_latest_command(request):
    command = Command.objects.last()
    if command:
        return JsonResponse({"command": command.command})
    return JsonResponse({})
def grafica(request):
    readings = Reading.objects.all().order_by('fecha')

    labels = []
    temperaturas = []
    turbidez = []
    conductividad = []

    for r in readings:
        labels.append(r.fecha.strftime("%H:%M"))
        temperaturas.append(r.temperatura)
        turbidez.append(r.turbidez)
        conductividad.append(r.conductividad)

    context = {
        "labels": labels,
        "temperaturas": temperaturas,
        "turbidez": turbidez,
        "conductividad": conductividad,
    }

    return render(request, "grafica.html", context)