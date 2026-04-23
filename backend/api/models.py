from django.db import models


class Device(models.Model):
    name        = models.CharField(max_length=100)
    ubicacion   = models.CharField(max_length=100, blank=True)
    mac_address = models.CharField(max_length=50, blank=True)
    activo      = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Dispositivo"
        verbose_name_plural = "Dispositivos"

    def __str__(self):
        return f"{self.name}"


class Reading(models.Model):
    device        = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="lecturas")
    temperatura   = models.FloatField()
    turbidez      = models.IntegerField()
    conductividad = models.IntegerField()
    ph            = models.FloatField()
    estado        = models.CharField(max_length=50)
    fecha         = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Lectura"
        verbose_name_plural = "Lecturas"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.device} | {self.temperatura}°C | {self.estado}"


class Command(models.Model):
    COMANDOS = [
        ("SINCRONIZAR",       "Sincronizar"),
        ("ACTIVAR_ALARMA",    "Activar alarma"),
        ("DESACTIVAR_ALARMA", "Desactivar alarma"),
        ("ENCENDER_FILTRADO", "Encender filtrado"),
        ("APAGAR_FILTRADO",   "Apagar filtrado"),
    ]

    device    = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="comandos")
    command   = models.CharField(max_length=100, choices=COMANDOS)
    ejecutado = models.BooleanField(default=False)
    fecha     = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Comando"
        verbose_name_plural = "Comandos"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.device} → {self.command}"


class Alert(models.Model):
    NIVELES = [
        ("VERDE",    "Verde"),
        ("AMARILLO", "Amarillo"),
        ("ROJO",     "Rojo"),
    ]

    device          = models.ForeignKey(Device,  on_delete=models.CASCADE, related_name="alertas")
    reading         = models.ForeignKey(Reading, on_delete=models.CASCADE, related_name="alertas")
    nivel_alerta    = models.CharField(max_length=20, choices=NIVELES)
    mensaje_estado  = models.CharField(max_length=50)
    mensaje_detalle = models.CharField(max_length=100)
    fecha           = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Alerta"
        verbose_name_plural = "Alertas"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.device} | {self.nivel_alerta}"


class Threshold(models.Model):
    device = models.OneToOneField(Device, on_delete=models.CASCADE, related_name="umbral")

    temp_max_peligro     = models.FloatField(default=60.0)
    temp_min_precaucion  = models.FloatField(default=10.0)

    turbidez_peligro     = models.IntegerField(default=600)
    turbidez_precaucion  = models.IntegerField(default=300)

    conductividad_peligro    = models.IntegerField(default=600)
    conductividad_precaucion = models.IntegerField(default=300)

    ph_min_peligro    = models.FloatField(default=4.0)
    ph_max_peligro    = models.FloatField(default=10.0)
    ph_min_precaucion = models.FloatField(default=6.0)
    ph_max_precaucion = models.FloatField(default=8.5)

    class Meta:
        verbose_name        = "Umbral"
        verbose_name_plural = "Umbrales"

    def __str__(self):
        return f"Umbrales de {self.device}"


class LogConexion(models.Model):
    EVENTOS = [
        ("CONECTADO",    "Conectado"),
        ("DESCONECTADO", "Desconectado"),
    ]

    device     = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="logs")
    evento     = models.CharField(max_length=50, choices=EVENTOS)
    ip_address = models.CharField(max_length=50, blank=True)
    fecha      = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = "Conexión"
        verbose_name_plural = "Conexiones de registro"
        ordering            = ["-fecha"]

    def __str__(self):
        return f"{self.device} | {self.evento}"