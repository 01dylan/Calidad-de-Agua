from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Device, Reading, Command, Alert, Threshold, LogConexion
import json


# =====================================================
#   DEVICES — CRUD COMPLETO
# =====================================================
def crud(request):
    return render(request, "crud.html")

def get_devices(request):
    data = list(Device.objects.values())
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_device(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data   = json.loads(request.body)
        device = Device.objects.create(
            name        = data["name"],
            ubicacion   = data.get("ubicacion", ""),
            mac_address = data.get("mac_address", ""),
            activo      = data.get("activo", True),
        )
        # Crear umbrales por defecto automáticamente
        Threshold.objects.create(device=device)
        return JsonResponse({"ok": True, "id": device.id, "name": device.name})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def update_device(request, device_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        device      = Device.objects.get(id=device_id)
        data        = json.loads(request.body)
        device.name        = data.get("name",        device.name)
        device.ubicacion   = data.get("ubicacion",   device.ubicacion)
        device.mac_address = data.get("mac_address", device.mac_address)
        device.activo      = data.get("activo",      device.activo)
        device.save()
        return JsonResponse({"ok": True})
    except Device.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def delete_device(request, device_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        Device.objects.get(id=device_id).delete()
        return JsonResponse({"ok": True})
    except Device.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)


# =====================================================
#   READINGS — CRUD COMPLETO
# =====================================================
def get_readings(request):
    device_id = request.GET.get("device_id")
    limit     = int(request.GET.get("limit", 20))
    qs        = Reading.objects.all()
    if device_id:
        qs = qs.filter(device_id=device_id)
    data = list(qs.values()[:limit])
    return JsonResponse(data, safe=False)


def get_latest_reading(request):
    device_id = request.GET.get("device_id")
    try:
        qs = Reading.objects.all()
        if device_id:
            qs = qs.filter(device_id=device_id)
        r = qs.latest("fecha")
        return JsonResponse({
            "id":            r.id,
            "device_id":     r.device_id,
            "temperatura":   r.temperatura,
            "turbidez":      r.turbidez,
            "conductividad": r.conductividad,
            "ph":            r.ph,
            "estado":        r.estado,
            "fecha":         r.fecha.strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Reading.DoesNotExist:
        return JsonResponse({"error": "Sin lecturas"}, status=404)


@csrf_exempt
def create_reading(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data   = json.loads(request.body)
        device = Device.objects.get(id=data["device_id"])

        try:
            th = device.umbral
        except Threshold.DoesNotExist:
            th = Threshold(
                temp_max_peligro=60,    temp_min_precaucion=10,
                turbidez_peligro=600,   turbidez_precaucion=300,
                conductividad_peligro=600, conductividad_precaucion=300,
                ph_min_peligro=4.0,     ph_max_peligro=10.0,
                ph_min_precaucion=6.0,  ph_max_precaucion=8.5,
            )

        temp = data["temperatura"]
        turb = data["turbidez"]
        cond = data["conductividad"]
        ph   = data["ph"]

        es_peligro = (
            temp >= th.temp_max_peligro or turb > th.turbidez_peligro or
            cond > th.conductividad_peligro or ph < th.ph_min_peligro or
            ph > th.ph_max_peligro
        )
        es_precaucion = (
            temp < th.temp_min_precaucion or turb > th.turbidez_precaucion or
            cond > th.conductividad_precaucion or ph < th.ph_min_precaucion or
            ph > th.ph_max_precaucion
        )

        if es_peligro:
            nivel, estado, detalle = "ROJO",    "ADVERTENCIA", "AGUA PELIGROSA"
        elif es_precaucion:
            nivel, estado, detalle = "AMARILLO", "PRECAUCION",  "Tenga cuidado"
        else:
            nivel, estado, detalle = "VERDE",   "AGUA APTA",   "Agua es segura"

        reading = Reading.objects.create(
            device=device, temperatura=temp,
            turbidez=turb, conductividad=cond, ph=ph, estado=estado,
        )
        Alert.objects.create(
            device=device, reading=reading,
            nivel_alerta=nivel, mensaje_estado=estado, mensaje_detalle=detalle,
        )
        return JsonResponse({"ok": True, "id": reading.id, "estado": estado, "nivel": nivel})

    except Device.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@csrf_exempt
def delete_reading(request, reading_id):
    if request.method != "DELETE":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        Reading.objects.get(id=reading_id).delete()
        return JsonResponse({"ok": True})
    except Reading.DoesNotExist:
        return JsonResponse({"error": "Lectura no encontrada"}, status=404)


# =====================================================
#   COMMANDS
# =====================================================
def get_commands(request):
    data = list(Command.objects.values()[:50])
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_command(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data    = json.loads(request.body)
        command = Command.objects.create(
            device_id=data["device_id"], command=data["command"],
        )
        return JsonResponse({"ok": True, "id": command.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_latest_command(request):
    device_id = request.GET.get("device_id")
    try:
        qs = Command.objects.filter(ejecutado=False)
        if device_id:
            qs = qs.filter(device_id=device_id)
        command          = qs.latest("fecha")
        command.ejecutado = True
        command.save()
        return JsonResponse({"command": command.command, "id": command.id})
    except Command.DoesNotExist:
        return JsonResponse({"command": None})


# =====================================================
#   ALERTS
# =====================================================
def get_alerts(request):
    device_id = request.GET.get("device_id")
    qs        = Alert.objects.all()
    if device_id:
        qs = qs.filter(device_id=device_id)
    data = list(qs.values()[:50])
    return JsonResponse(data, safe=False)


# =====================================================
#   THRESHOLDS — CRUD
# =====================================================
def get_threshold(request):
    device_id = request.GET.get("device_id")
    try:
        th = Threshold.objects.get(device_id=device_id)
        return JsonResponse({
            "temp_max_peligro":          th.temp_max_peligro,
            "temp_min_precaucion":       th.temp_min_precaucion,
            "turbidez_peligro":          th.turbidez_peligro,
            "turbidez_precaucion":       th.turbidez_precaucion,
            "conductividad_peligro":     th.conductividad_peligro,
            "conductividad_precaucion":  th.conductividad_precaucion,
            "ph_min_peligro":            th.ph_min_peligro,
            "ph_max_peligro":            th.ph_max_peligro,
            "ph_min_precaucion":         th.ph_min_precaucion,
            "ph_max_precaucion":         th.ph_max_precaucion,
        })
    except Threshold.DoesNotExist:
        return JsonResponse({"error": "Sin umbrales"}, status=404)


@csrf_exempt
def update_threshold(request, device_id):
    if request.method != "PUT":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        th   = Threshold.objects.get(device_id=device_id)
        data = json.loads(request.body)
        for campo in [
            "temp_max_peligro", "temp_min_precaucion",
            "turbidez_peligro", "turbidez_precaucion",
            "conductividad_peligro", "conductividad_precaucion",
            "ph_min_peligro", "ph_max_peligro",
            "ph_min_precaucion", "ph_max_precaucion",
        ]:
            if campo in data:
                setattr(th, campo, data[campo])
        th.save()
        return JsonResponse({"ok": True})
    except Threshold.DoesNotExist:
        return JsonResponse({"error": "Sin umbrales"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# =====================================================
#   LOG CONEXION
# =====================================================
@csrf_exempt
def create_log(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)
    try:
        data = json.loads(request.body)
        log  = LogConexion.objects.create(
            device_id  = data["device_id"],
            evento     = data["evento"],
            ip_address = data.get("ip_address", ""),
        )
        return JsonResponse({"ok": True, "id": log.id})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


# =====================================================
#   DASHBOARD + GRAFICA
# =====================================================
def dashboard(request):
    return render(request, "dashboard.html")


def grafica(request):
    return render(request, "grafica.html")