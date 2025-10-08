from .models import Cart

def cart_context(request):

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return {'cart': cart}
    return {'cart': None}

