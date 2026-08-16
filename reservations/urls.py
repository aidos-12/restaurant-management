from django.urls import path

from .views import (
    reservation_create,
    reservation_success,
    my_reservations,
    tables,
    cancel_reservation,
    employee_reservations,
    update_reservation_status,
)


urlpatterns = [

    path(
        '',
        tables,
        name='tables'
    ),

    path(
        'book/<int:table_id>/',
        reservation_create,
        name='reservation_create'
    ),

    path(
        'success/<int:reservation_id>/',
        reservation_success,
        name='reservation_success'
    ),

    path(
        'my/',
        my_reservations,
        name='my_reservations'
    ),

    path(
        'cancel/<int:reservation_id>/',
        cancel_reservation,
        name='cancel_reservation'
    ),

    path(
        'employee/',
        employee_reservations,
        name='employee_reservations'
    ),

    path(
    'employee/<int:reservation_id>/status/',
    update_reservation_status,
    name='update_reservation_status'
),
]