from django.shortcuts import redirect, render
from django.shortcuts import HttpResponse


def isathenticated_user(actual_func):
    def inner_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.groups.exists():
                if request.user.groups.all()[0].name == 'admin' or request.user.groups.all()[0].name == 'stockist':
                    return redirect('dashboard')
                else:
                    return redirect('gameconsole')
        else:
            return actual_func(request, *args, **kwargs)
    return inner_func


def authorized_user(allowed_roles=[]):
    def decorator(actual_func):
        def inner_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name

            if group in allowed_roles:
                return actual_func(request, *args, **kwargs)
            else:
                return render(request, 'deskapp/401.html')
        return inner_func
    return decorator
