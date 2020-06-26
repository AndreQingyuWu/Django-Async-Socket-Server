# Register your models here.
from django.contrib import admin
from .models import User, Device, Data, Warning, Option, Timedtask, Upload

admin.site.register(User)
admin.site.register(Device)
admin.site.register(Data)
admin.site.register(Warning)
admin.site.register(Option)
admin.site.register(Timedtask)
admin.site.register(Upload)
