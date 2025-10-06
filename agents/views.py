from django.shortcuts import render
from django.http import JsonResponse
from .models import Agent


def _distance_km(a_lat: float, a_lng: float, b_lat: float, b_lng: float) -> float:
    from math import asin, sqrt, sin, cos, pi
    R = 6371.0
    d_lat = (b_lat - a_lat) * pi / 180.0
    d_lng = (b_lng - a_lng) * pi / 180.0
    la1 = a_lat * pi / 180.0
    la2 = b_lat * pi / 180.0
    x = sin(d_lat/2)**2 + sin(d_lng/2)**2 * cos(la1) * cos(la2)
    return 2 * R * asin(sqrt(x))


def agent_list(request):
    agents = Agent.objects.filter(is_active=True).select_related('user', 'center')
    return render(request, 'agents/agent_list.html', {'agents': agents})


def nearest_agents(request):
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return JsonResponse({'error': 'Invalid or missing lat/lng'}, status=400)
    limit = int(request.GET.get('limit', 5))
    agents = Agent.objects.filter(is_active=True).select_related('user', 'center')
    enriched = []
    for ag in agents:
        c = ag.center
        d = _distance_km(lat, lng, c.latitude, c.longitude)
        enriched.append((d, ag))
    enriched.sort(key=lambda x: x[0])
    data = []
    for d, ag in enriched[:limit]:
        data.append({
            'id': ag.id,
            'name': ag.user.get_full_name() or ag.user.get_username(),
            'phone': ag.phone,
            'center': ag.center.name,
            'center_id': ag.center.id,
            'distance_km': round(d, 2),
        })
    return JsonResponse({'agents': data})

# Create your views here.
