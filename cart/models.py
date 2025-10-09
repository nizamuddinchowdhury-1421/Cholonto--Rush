from django.db import models
from django.contrib.auth import get_user_model
from services.models import Service

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Cart of {self.user.get_username()}"
    
    @property
    def total(self):
        """Calculate total amount for all items in cart"""
        return sum(item.line_total() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def line_total(self):
        return self.quantity * self.service.base_price

# Create your models here.
