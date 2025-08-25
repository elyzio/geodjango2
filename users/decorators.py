from django.shortcuts import render
from functools import wraps

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper_func(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return render(request, 'main/auth/404.html')  # Or redirect to login

            user_groups = request.user.groups.values_list('name', flat=True)

            if any(group in allowed_roles for group in user_groups):
                return view_func(request, *args, **kwargs)
            else:
                return render(request, 'auth/404.html')  # Or 'no permission'
        return wrapper_func
    return decorator
