from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import employee_required

from .forms import ReservationForm
from .models import Reservation, Table
from .services import (
    cancel_reservation as cancel_reservation_service,
    create_reservation,
)


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

            try:

                reservation = create_reservation(
                    customer=request.user,
                    table=table,
                    date=form.cleaned_data['date'],
                    time=form.cleaned_data['time'],
                    guests=form.cleaned_data['guests'],
                    comment=form.cleaned_data['comment'],
                )

                return redirect(
                    'reservation_success',
                    reservation_id=reservation.id
                )

            except ValidationError as error:

                form.add_error(
                    None,
                    error.message
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

        try:

            cancel_reservation_service(
                reservation
            )

        except ValidationError:

            pass

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

        valid_statuses = dict(
            Reservation.Status.choices
        )

        if new_status in valid_statuses:

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

            reservation.save(
                update_fields=['status']
            )

    return redirect(
        'employee_reservations'
    )