from django.shortcuts import render
from .models import ServiceCenter


def center_list(request):
    centers = ServiceCenter.objects.filter(is_active=True)
    return render(request, 'centers/center_list.html', {'centers': centers})

# Create your views here.
