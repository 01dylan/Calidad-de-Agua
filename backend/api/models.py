from django.db import models


# DEVICE

class Device(models.Model):
    name = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=100, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    activo = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    class meta:
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
def __str__(self):
        return f"{self.name}"


# READING

class Reading(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    temperatura = models.FloatField()
    turbidez = models.IntegerField()
    conductividad = models.IntegerField()
    ph = models.FloatField()
    estado = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Lectura"
        verbose_name_plural = "Lecturas"
def __str__(self):
        return f"{self.device}- {self.temperatura} "

# COMMAND

class Command(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    command = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)


class Meta:
        verbose_name = "Comando"
        verbose_name_plural = "Comandos"


# ALERT

class Alert(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    reading = models.ForeignKey(Reading, on_delete=models.CASCADE)

    nivel_alerta = models.CharField(max_length=20)
    mensaje_estado = models.CharField(max_length=50)
    mensaje_detalle = models.CharField(max_length=100)

    fecha = models.DateTimeField(auto_now_add=True)
class Meta:
        verbose_name = "Alerta"
        verbose_name_plural = "Alertas"


# THRESHOLD

class Threshold(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)

    temp_max_peligro = models.FloatField()
    temp_min_precaucion = models.FloatField()

    turbidez_peligro = models.IntegerField()
    turbidez_precaucion = models.IntegerField()

    conductividad_peligro = models.IntegerField()
    conductividad_precaucion = models.IntegerField()
class Meta:
        verbose_name = "Umbral"
        verbose_name_plural = "Umbrales"


# LOG

class LogConexion(models.Model):
    device = models.ForeignKey(Device, on_delete=models.CASCADE)
    evento = models.CharField(max_length=50)
    ip_address = models.CharField(max_length=50)
    fecha = models.DateTimeField(auto_now_add=True)
class Meta:
        verbose_name = "Conexión"
        verbose_name_plural = "Conexiones de registro"