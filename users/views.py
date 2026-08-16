from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import render, redirect

from .forms import RegisterForm

from orders.models import Order
from reservations.models import Reservation


def home(request):
    is_employee = (
        request.user.is_authenticated
        and request.user.groups.filter(
            name='Сотрудник'
        ).exists()
    )

    return render(
        request,
        'users/home.html',
        {
            'is_employee': is_employee,
        }
    )


def register(request):

    if request.method == 'POST':

        form = RegisterForm(request.POST)

        if form.is_valid():

            with transaction.atomic():

                user = form.save()

                client_group, created = Group.objects.get_or_create(
                    name='Клиент'
                )

                user.groups.add(client_group)

            login(request, user)

            return redirect('home')

    else:

        form = RegisterForm()

    return render(
        request,
        'users/register.html',
        {
            'form': form,
        }
    )


def login_view(request):

    if request.method == 'POST':

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(request, user)

            if user.groups.filter(
                name='Сотрудник'
            ).exists():

                return redirect(
                    'employee_orders'
                )

            return redirect('home')

    else:

        form = AuthenticationForm()

    return render(
        request,
        'users/login.html',
        {
            'form': form,
        }
    )


def logout_view(request):

    logout(request)

    return redirect('home')


@login_required
def profile(request):

    orders_count = Order.objects.filter(
        customer=request.user
    ).count()

    active_reservations_count = Reservation.objects.filter(
        customer=request.user,
        status__in=[
            Reservation.Status.PENDING,
            Reservation.Status.CONFIRMED,
        ]
    ).count()

    return render(
        request,
        'users/profile.html',
        {
            'orders_count': orders_count,
            'active_reservations_count': active_reservations_count,
        }
    )


@login_required
def order_history(request):

    orders = Order.objects.filter(
        customer=request.user
    ).prefetch_related(
        'items__product'
    ).order_by(
        '-created_at'
    )

    paginator = Paginator(orders, 10)

    page_number = request.GET.get('page')

    page_obj = paginator.get_page(page_number)

    return render(
        request,
        'users/order_history.html',
        {
            'page_obj': page_obj,
        }
    )