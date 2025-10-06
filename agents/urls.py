from django.urls import path
from . import views

urlpatterns = [
    path('', views.agent_list, name='agent_list'),
    path('nearest/', views.nearest_agents, name='nearest_agents'),
]

