from django.urls import path
from . import views

urlpatterns = [
    path('', views.center_list, name='center_list'),
]

