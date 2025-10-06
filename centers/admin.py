from django.contrib import admin
from .models import ServiceCenter


@admin.register(ServiceCenter)
class ServiceCenterAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "address", "is_active")
    list_filter = ("is_active",)

# Register your models here.
