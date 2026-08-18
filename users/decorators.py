from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def employee_required(view_func):

    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='Сотрудник'
        ).exists():

            return render(
                request,
                'users/access_denied.html',
                status=403
            )

        return view_func(
            request,
            *args,
            **kwargs
        )

    return wrapper