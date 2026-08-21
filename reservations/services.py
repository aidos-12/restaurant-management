from datetime import datetime

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from .models import Reservation


def create_reservation(
    *,
    customer,
    table,
    date,
    time,
    guests,
    comment=''
):
    if not table.is_available:
        raise ValidationError(
            f'Столик №{table.number} сейчас недоступен.'
        )

    reservation = Reservation(
        customer=customer,
        table=table,
        date=date,
        time=time,
        guests=guests,
        comment=comment,
    )

    reservation_datetime = timezone.make_aware(
        datetime.combine(
            date,
            time
        )
    )

    if reservation_datetime < timezone.now():
        raise ValidationError(
            'Нельзя создать бронирование '
            'на прошедшие дату и время.'
        )

    if guests > table.seats:
        raise ValidationError(
            f'За столиком только {table.seats} мест.'
        )

    with transaction.atomic():

        conflict_exists = Reservation.objects.filter(
            table=table,
            date=date,
            time=time,
            status__in=[
                Reservation.Status.PENDING,
                Reservation.Status.CONFIRMED,
            ]
        ).exists()

        if conflict_exists:
            raise ValidationError(
                'Этот столик уже забронирован '
                'на выбранное время.'
            )

        reservation.full_clean()
        reservation.save()

    return reservation


def cancel_reservation(reservation):

    cancellable_statuses = [
        Reservation.Status.PENDING,
        Reservation.Status.CONFIRMED,
    ]

    if reservation.status not in cancellable_statuses:
        raise ValidationError(
            'Это бронирование нельзя отменить.'
        )

    reservation.status = Reservation.Status.CANCELLED

    reservation.save(
        update_fields=['status']
    )

    return reservation