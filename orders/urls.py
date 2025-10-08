from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.checkout, name='checkout'),
    path('book/', views.book_services, name='book_services'),
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('my/', views.my_orders, name='my_orders'),
    path('<int:order_id>/', views.order_detail, name='order_detail'),
]

