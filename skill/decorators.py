from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps

def authenticated_user(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return _wrapped_view



def logout_required(view_func):
    """
    Décorateur pour restreindre l'accès aux vues aux utilisateurs déconnectés.
    Si l'utilisateur est connecté, il sera redirigé vers la page d'accueil.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(reverse('home'))
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles=[]):
    """
    Décorateur pour restreindre l'accès aux vues selon le rôle des utilisateurs.
    :param allowed_roles: Liste des rôles autorisés pour accéder à la vue.
    """
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.role in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # Redirige vers une page d'erreur ou d'accès refusé
                return redirect(reverse('access_denied'))
        return _wrapped_view
    return decorator
