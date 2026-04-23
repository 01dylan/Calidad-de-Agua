from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import Device, Reading, Command, Alert, Threshold, LogConexion
import json


# =====================================================
#   DEVICES
# =====================================================
def get_devices(request):
    data = list(Device.objects.values())
    return JsonResponse(data, safe=False)


# =====================================================
#   READINGS
# =====================================================
def get_readings(request):
    device_id = request.GET.get("device_id")
    limit     = int(request.GET.get("limit", 20))

    qs = Reading.objects.all()
    if device_id:
        qs = qs.filter(device_id=device_id)

    data = list(qs.values()[:limit])
    return JsonResponse(data, safe=False)


@csrf_exempt
def create_reading(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    try:
        data    = json.loads(request.body)
        device  = Device.objects.get(id=data["device_id"])

        # Obtener umbrales del dispositivo (o usar defaults)
        try:
            th = device.umbral
        except Threshold.DoesNotExist:
            th = Threshold(
                temp_max_peligro=60, temp_min_precaucion=10,
                turbidez_peligro=600, turbidez_precaucion=300,
                conductividad_peligro=600, conductividad_precaucion=300,
                ph_min_peligro=4.0, ph_max_peligro=10.0,
                ph_min_precaucion=6.0, ph_max_precaucion=8.5,
            )

        temp  = data["temperatura"]
        turb  = data["turbidez"]
        cond  = data["conductividad"]
        ph    = data["ph"]

        # Determinar estado automáticamente
        es_peligro = (
            temp >= th.temp_max_peligro or
            turb > th.turbidez_peligro or
            cond > th.conductividad_peligro or
            ph < th.ph_min_peligro or
            ph > th.ph_max_peligro
        )
        es_precaucion = (
            temp < th.temp_min_precaucion or
            turb > th.turbidez_precaucion or
            cond > th.conductividad_precaucion or
            ph < th.ph_min_precaucion or
            ph > th.ph_max_precaucion
        )

        if es_peligro:
            nivel   = "ROJO"
            estado  = "ADVERTENCIA"
            detalle = "AGUA PELIGROSA"
        elif es_precaucion:
            nivel   = "AMARILLO"
            estado  = "PRECAUCION"
            detalle = "Tenga cuidado"
        else:
            nivel   = "VERDE"
            estado  = "AGUA APTA"
            detalle = "Agua es segura"

        # Guardar lectura
        reading = Reading.objects.create(
            device        = device,
            temperatura   = temp,
            turbidez      = turb,
            conductividad = cond,
            ph            = ph,
            estado        = estado,
        )

        # Guardar alerta automática
        Alert.objects.create(
            device          = device,
            reading         = reading,
            nivel_alerta    = nivel,
            mensaje_estado  = estado,
            mensaje_detalle = detalle,
        )

        return JsonResponse({
            "ok":     True,
            "id":     reading.id,
            "estado": estado,
            "nivel":  nivel,
        })

    except Device.DoesNotExist:
        return JsonResponse({"error": "Dispositivo no encontrado"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


def get_latest_reading(request):
    device_id = request.GET.get("device_id")
    try:
        qs = Reading.objects.all()
        if device_id:
            qs = qs.filter(device_id=device_id)
        reading = qs.latest("fecha")
        return JsonResponse({
            "id":           reading.id,
            "device_id":    reading.device_id,
            "temperatura":  reading.temperatura,
            "turbidez":     reading.turbidez,
            "conductividad":reading.conductividad,
            "ph":           reading.ph,
            "estado":       reading.estado,
            "fecha":        reading.fecha.strftime("%Y-%m-%d %H:%M:%S"),
        })
    except Reading.DoesNotExist:
        return JsonResponse({"error": "Sin lecturas"}, status=404)


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
            device_id = data["device_id"],
            command   = data["command"],
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
        command = qs.latest("fecha")

        # Marcarlo como ejecutado
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
    qs = Alert.objects.all()
    if device_id:
        qs = qs.filter(device_id=device_id)
    data = list(qs.values()[:50])
    return JsonResponse(data, safe=False)


# =====================================================
#   THRESHOLDS
# =====================================================
def get_threshold(request):
    device_id = request.GET.get("device_id")
    try:
        th = Threshold.objects.get(device_id=device_id)
        return JsonResponse({
            "temp_max_peligro":       th.temp_max_peligro,
            "temp_min_precaucion":    th.temp_min_precaucion,
            "turbidez_peligro":       th.turbidez_peligro,
            "turbidez_precaucion":    th.turbidez_precaucion,
            "conductividad_peligro":  th.conductividad_peligro,
            "conductividad_precaucion": th.conductividad_precaucion,
            "ph_min_peligro":         th.ph_min_peligro,
            "ph_max_peligro":         th.ph_max_peligro,
            "ph_min_precaucion":      th.ph_min_precaucion,
            "ph_max_precaucion":      th.ph_max_precaucion,
        })
    except Threshold.DoesNotExist:
        return JsonResponse({"error": "Sin umbrales configurados"}, status=404)


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
#   DASHBOARD (HTML)
# =====================================================
def dashboard(request):
    devices  = Device.objects.filter(activo=True)
    device_id = request.GET.get("device_id")

    lecturas     = []
    ultima       = None
    ultima_alerta = None
    device_sel   = None

    if device_id:
        try:
            device_sel    = Device.objects.get(id=device_id)
            lecturas      = Reading.objects.filter(device_id=device_id)[:20]
            ultima        = lecturas[0] if lecturas else None
            ultima_alerta = Alert.objects.filter(device_id=device_id).first()
        except Device.DoesNotExist:
            pass

    context = {
        "devices":       devices,
        "device_sel":    device_sel,
        "lecturas":      lecturas,
        "ultima":        ultima,
        "ultima_alerta": ultima_alerta,
    }
    return render(request, "dashboard.html", context)


# =====================================================
#   GRÁFICA (HTML)
# =====================================================
def grafica(request):
    device_id = request.GET.get("device_id")
    readings  = Reading.objects.all().order_by("fecha")
    if device_id:
        readings = readings.filter(device_id=device_id)

    labels        = [r.fecha.strftime("%H:%M") for r in readings]
    temperaturas  = [r.temperatura   for r in readings]
    turbidez      = [r.turbidez      for r in readings]
    conductividad = [r.conductividad for r in readings]
    ph            = [r.ph            for r in readings]

    return render(request, "grafica.html", {
        "labels":        json.dumps(labels),
        "temperaturas":  json.dumps(temperaturas),
        "turbidez":      json.dumps(turbidez),
        "conductividad": json.dumps(conductividad),
        "ph":            json.dumps(ph),
    })