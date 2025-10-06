from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from cart.models import CartItem
from agents.models import Agent
from math import asin, sqrt, sin, cos, pi
from .models import Order, OrderItem
from centers.models import ServiceCenter


@login_required
def checkout(request):
    items = CartItem.objects.filter(cart__user=request.user).select_related('service')
    total = sum([it.quantity * it.service.base_price for it in items])
    centers = ServiceCenter.objects.filter(is_active=True)
    return render(request, 'orders/checkout.html', {'items': items, 'total': total, 'centers': centers})


@login_required
@transaction.atomic
def book_services(request):
    if request.method != 'POST':
        return redirect('checkout')
    center_id = request.POST.get('center_id')
    lat = request.POST.get('lat')
    lng = request.POST.get('lng')
    center = ServiceCenter.objects.filter(pk=center_id).first()
    items = CartItem.objects.filter(cart__user=request.user).select_related('service')
    total = sum([it.quantity * it.service.base_price for it in items])
    order = Order.objects.create(user=request.user, center=center, total_amount=total, status='pending')
    # Assign nearest agent if user location present
    try:
        lat_f = float(lat)
        lng_f = float(lng)
        agents = Agent.objects.filter(is_active=True, center=center).select_related('center')
        def dist(a_lat, a_lng, b_lat, b_lng):
            d_lat = (b_lat - a_lat) * pi / 180.0
            d_lng = (b_lng - a_lng) * pi / 180.0
            la1 = a_lat * pi / 180.0
            la2 = b_lat * pi / 180.0
            x = sin(d_lat/2)**2 + sin(d_lng/2)**2 * cos(la1) * cos(la2)
            return 2 * 6371.0 * asin(sqrt(x))
        best = None
        best_d = 1e9
        for ag in agents:
            c = ag.center
            d = dist(lat_f, lng_f, c.latitude, c.longitude)
            if d < best_d:
                best_d = d
                best = ag
        if best:
            order.assigned_agent = best
            order.status = 'assigned'
            order.save()
    except (TypeError, ValueError):
        pass
    for it in items:
        OrderItem.objects.create(order=order, service=it.service, quantity=it.quantity, price=it.service.base_price)
    items.delete()
    return redirect('home')

@login_required
def my_orders(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__service', 'center', 'assigned_agent')
    return render(request, 'orders/my_orders.html', {'orders': orders})


@login_required
def order_detail(request, order_id: int):
    order = Order.objects.filter(id=order_id, user=request.user).prefetch_related('items__service', 'center', 'assigned_agent').first()
    if not order:
        return redirect('my_orders')
    return render(request, 'orders/order_detail.html', {'order': order})
