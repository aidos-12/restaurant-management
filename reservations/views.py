from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import employee_required

from .forms import ReservationForm
from .models import Table, Reservation


@login_required
def reservation_create(request, table_id):

    table = get_object_or_404(
        Table,
        id=table_id,
        is_available=True
    )

    if request.method == 'POST':

        reservation = Reservation(
            customer=request.user,
            table=table
        )

        form = ReservationForm(
            request.POST,
            instance=reservation
        )

        if form.is_valid():

            with transaction.atomic():

                conflict_exists = Reservation.objects.filter(
                    table=table,
                    date=reservation.date,
                    time=reservation.time,
                    status__in=[
                        Reservation.Status.PENDING,
                        Reservation.Status.CONFIRMED,
                    ]
                ).exists()

                if conflict_exists:

                    form.add_error(
                        None,
                        'Этот столик уже забронирован '
                        'на выбранное время.'
                    )

                else:

                    reservation.save()

                    return redirect(
                        'reservation_success',
                        reservation_id=reservation.id
                    )

    else:

        reservation = Reservation(
            customer=request.user,
            table=table
        )

        form = ReservationForm(
            instance=reservation
        )

    return render(
        request,
        'reservations/booking.html',
        {
            'form': form,
            'table': table,
        }
    )


@login_required
def reservation_success(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        customer=request.user
    )

    return render(
        request,
        'reservations/success.html',
        {
            'reservation': reservation,
        }
    )


@login_required
def my_reservations(request):

    reservations = Reservation.objects.filter(
        customer=request.user
    ).select_related(
        'table'
    )

    return render(
        request,
        'reservations/my_reservations.html',
        {
            'reservations': reservations,
        }
    )


def tables(request):

    tables = Table.objects.filter(
        is_available=True
    )

    return render(
        request,
        'reservations/tables.html',
        {
            'tables': tables,
        }
    )


@login_required
def cancel_reservation(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id,
        customer=request.user
    )

    if request.method == 'POST':

        cancellable_statuses = [
            Reservation.Status.PENDING,
            Reservation.Status.CONFIRMED,
        ]

        if reservation.status in cancellable_statuses:

            reservation.status = Reservation.Status.CANCELLED
            reservation.save()

    return redirect(
        'my_reservations'
    )


@employee_required
def employee_reservations(request):

    reservations = Reservation.objects.select_related(
        'customer',
        'table'
    ).order_by(
        '-date',
        '-time'
    )

    return render(
        request,
        'reservations/employee_reservations.html',
        {
            'reservations': reservations,
            'status_choices': Reservation.Status.choices,
        }
    )


@employee_required
def update_reservation_status(request, reservation_id):

    reservation = get_object_or_404(
        Reservation,
        id=reservation_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        valid_statuses = dict(
            Reservation.Status.choices
        )

        if new_status in valid_statuses:

            allowed_transitions = {
                Reservation.Status.PENDING: [
                    Reservation.Status.CONFIRMED,
                    Reservation.Status.CANCELLED,
                ],

                Reservation.Status.CONFIRMED: [
                    Reservation.Status.COMPLETED,
                    Reservation.Status.CANCELLED,
                ],

                Reservation.Status.COMPLETED: [],

                Reservation.Status.CANCELLED: [],
            }

            if new_status not in allowed_transitions.get(
                reservation.status,
                []
            ):

                return render(
                    request,
                    'users/access_denied.html',
                    {
                        'error':
                            'Недопустимый переход статуса '
                            'бронирования.'
                    },
                    status=400
                )

            reservation.status = new_status
            reservation.save()

    return redirect(
        'employee_reservations'
    )