from django.contrib import admin
from .models import IPPrefix, IPSubnets

admin.site.register(IPPrefix)
admin.site.register(IPSubnets)
