from django.contrib import admin
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ("user", "center", "phone", "is_active")
    list_filter = ("is_active", "center")

# Register your models here.
