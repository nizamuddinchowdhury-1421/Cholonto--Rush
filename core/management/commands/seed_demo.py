from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from services.models import ServiceCategory, Service
from centers.models import ServiceCenter
from agents.models import Agent


class Command(BaseCommand):
    help = "Seed demo data for TukTuk"

    def handle(self, *args, **options):
        cat_basic, _ = ServiceCategory.objects.get_or_create(name="Basic Maintenance",
                                                             defaults={"description": "Basic roadside maintenance"})
        cat_emerg, _ = ServiceCategory.objects.get_or_create(name="Emergency",
                                                             defaults={"description": "Emergency help"})

        Service.objects.get_or_create(name="Flat Tyre Fix", defaults={
            "description": "Puncture repair and tube replacement",
            "category": cat_basic,
            "base_price": 199,
            "is_active": True,
        })
        Service.objects.get_or_create(name="Battery Jumpstart", defaults={
            "description": "Jumpstart and battery health check",
            "category": cat_emerg,
            "base_price": 299,
            "is_active": True,
        })
        Service.objects.get_or_create(name="Oil Top-up", defaults={
            "description": "Engine oil top-up",
            "category": cat_basic,
            "base_price": 149,
            "is_active": True,
        })

        c1, _ = ServiceCenter.objects.get_or_create(name="Dhaka Bikes Service",
                                                     defaults={
                                                         "phone": "+8801712345678",
                                                         "address": "Banani, Dhaka",
                                                         "latitude": 23.7925,
                                                         "longitude": 90.4078,
                                                         "is_active": True,
                                                     })
        c2, _ = ServiceCenter.objects.get_or_create(name="Chattogram Riders Hub",
                                                     defaults={
                                                         "phone": "+8801812345678",
                                                         "address": "GEC Circle, Chattogram",
                                                         "latitude": 22.3595,
                                                         "longitude": 91.8212,
                                                         "is_active": True,
                                                     })

        if not User.objects.filter(username="agent1").exists():
            u = User.objects.create_user(username="agent1", password="agent1pass", first_name="Arafat")
            Agent.objects.create(user=u, center=c1, phone="+8801712345679", is_active=True)

        self.stdout.write(self.style.SUCCESS("Seed data created/updated."))

