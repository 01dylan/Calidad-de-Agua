from django.contrib import admin
from .models import *

admin.site.register(Device)
admin.site.register(Reading)
admin.site.register(Command)
admin.site.register(Alert)
admin.site.register(Threshold)
admin.site.register(LogConexion)