from django.db import models
from django.contrib.auth import get_user_model
from centers.models import ServiceCenter

User = get_user_model()


class Agent(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    center = models.ForeignKey(ServiceCenter, on_delete=models.CASCADE, related_name='agents')
    phone = models.CharField(max_length=20)
    is_active = models.BooleanField(default=True)

    def __str__(self) -> str:
        return f"{self.user.get_username()} ({self.center.name})"

# Create your models here.
