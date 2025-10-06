from django.db import models


class ServiceCenter(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

# Create your models here.
