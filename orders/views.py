from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
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
    payment_method = request.POST.get('payment_method', 'cash')
    center = ServiceCenter.objects.filter(pk=center_id).first()
    items = CartItem.objects.filter(cart__user=request.user).select_related('service')
    total = sum([it.quantity * it.service.base_price for it in items])
    
    # Set order status based on payment method
    status = 'confirmed' if payment_method == 'cash' else 'pending'
    order = Order.objects.create(user=request.user, center=center, total_amount=total, status=status)
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
            # Only change status to 'assigned' for cash payments
            # Keep 'pending' status for online payments until payment is completed
            if payment_method == 'cash':
                order.status = 'assigned'
                order.save()
    except (TypeError, ValueError):
        pass
    for it in items:
        OrderItem.objects.create(order=order, service=it.service, quantity=it.quantity, price=it.service.base_price)
    
    # Clear cart items after creating order (for both cash and online payments)
    items.delete()
    
    # Redirect based on payment method
    if payment_method == 'cash':
        messages.success(request, 'Service booked successfully! You will pay cash when the service is provided.')
        return redirect('my_orders')
    else:
        return redirect('payment')

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


@login_required
def payment(request):
    # Get the latest pending order for this user (cart is already cleared)
    latest_pending_order = Order.objects.filter(user=request.user, status='pending').order_by('-created_at').first()
    
    if latest_pending_order:
        total = latest_pending_order.total_amount
        order = latest_pending_order
    else:
        # Fallback: try to calculate from cart items if no pending order found
        items = CartItem.objects.filter(cart__user=request.user).select_related('service')
        total = sum([it.quantity * it.service.base_price for it in items])
        order = None
    
    return render(request, 'orders/payment.html', {'total': total, 'order': order})


@login_required
def payment_success(request):
    # Get the latest pending order for this user and mark it as confirmed
    latest_pending_order = Order.objects.filter(user=request.user, status='pending').order_by('-created_at').first()
    
    if latest_pending_order:
        # Mark as confirmed
        latest_pending_order.status = 'confirmed'
        latest_pending_order.save()
        
        # Clear cart items to ensure cart is empty after payment success
        CartItem.objects.filter(cart__user=request.user).delete()
        
        # Debug logging
        print(f"Payment Success - Pending Order: #{latest_pending_order.id}, Amount: {latest_pending_order.total_amount}")
        for item in latest_pending_order.items.all():
            print(f"  - {item.service.name}: {item.quantity} x Tk {item.price} = Tk {item.line_total()}")
        
        messages.success(request, 'Payment successful! Your service booking has been confirmed.')
        
        return render(request, 'orders/payment_success.html', {
            'order_id': latest_pending_order.id,
            'total': latest_pending_order.total_amount,
            'order': latest_pending_order
        })
    else:
        # If no pending order found, check for the most recent order (might already be confirmed)
        latest_order = Order.objects.filter(user=request.user).order_by('-created_at').first()
        if latest_order:
            # Clear cart items to ensure cart is empty after payment success
            CartItem.objects.filter(cart__user=request.user).delete()
            
            # Debug logging
            print(f"Payment Success - Fallback Order: #{latest_order.id}, Amount: {latest_order.total_amount}")
            for item in latest_order.items.all():
                print(f"  - {item.service.name}: {item.quantity} x Tk {item.price} = Tk {item.line_total()}")
            
            messages.success(request, 'Payment successful! Your service booking has been confirmed.')
            return render(request, 'orders/payment_success.html', {
                'order_id': latest_order.id,
                'total': latest_order.total_amount,
                'order': latest_order
            })
        else:
            # If no orders found at all, redirect to orders page
            messages.error(request, 'No order found. Please try again.')
            return redirect('my_orders')
