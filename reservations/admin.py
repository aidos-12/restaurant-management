from django.contrib import admin

from .models import Table, Reservation


@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = (
        'number',
        'seats',
        'is_available',
    )

    list_filter = (
        'is_available',
    )

    ordering = (
        'number',
    )


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'table',
        'date',
        'time',
        'guests',
        'status',
    )

    list_filter = (
        'status',
        'date',
    )

    search_fields = (
        'customer__username',
        'customer__email',
    )

    ordering = (
        '-date',
        '-time',
    )