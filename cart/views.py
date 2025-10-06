from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem
from services.models import Service


def _get_or_create_cart(user):
    cart, _ = Cart.objects.get_or_create(user=user)
    return cart


@login_required
def view_cart(request):
    cart = _get_or_create_cart(request.user)
    return render(request, 'cart/view_cart.html', {'cart': cart})


@login_required
def add_to_cart(request, service_id: int):
    cart = _get_or_create_cart(request.user)
    service = get_object_or_404(Service, pk=service_id, is_active=True)
    item, created = CartItem.objects.get_or_create(cart=cart, service=service)
    if not created:
        item.quantity += 1
        item.save()
    return redirect('view_cart')


@login_required
def remove_from_cart(request, item_id: int):
    cart = _get_or_create_cart(request.user)
    item = get_object_or_404(CartItem, pk=item_id, cart=cart)
    item.delete()
    return redirect('view_cart')

# Create your views here.
