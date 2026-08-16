from datetime import datetime

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Table(models.Model):

    number = models.PositiveIntegerField(
        unique=True,
        verbose_name='Номер стола'
    )

    seats = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Количество мест'
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name='Доступен'
    )

    class Meta:
        verbose_name = 'Столик'
        verbose_name_plural = 'Столики'
        ordering = ['number']

    def __str__(self):
        return f'Столик №{self.number} ({self.seats} мест)'


class Reservation(models.Model):

    class Status(models.TextChoices):
        PENDING = 'pending', 'Ожидает подтверждения'
        CONFIRMED = 'confirmed', 'Подтверждено'
        COMPLETED = 'completed', 'Завершено'
        CANCELLED = 'cancelled', 'Отменено'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='reservations',
        verbose_name='Клиент'
    )

    table = models.ForeignKey(
        Table,
        on_delete=models.PROTECT,
        related_name='reservations',
        verbose_name='Столик'
    )

    date = models.DateField(
        verbose_name='Дата'
    )

    time = models.TimeField(
        verbose_name='Время'
    )

    guests = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1)
        ],
        verbose_name='Количество гостей'
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name='Статус'
    )

    comment = models.TextField(
        blank=True,
        verbose_name='Комментарий'
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Бронирование'
        verbose_name_plural = 'Бронирования'
        ordering = ['-date', '-time']

    def clean(self):

        if not self.table_id:
            raise ValidationError(
                'Необходимо выбрать столик.'
            )

        # Проверяем доступность столика только
        # при создании новой брони.
        if self._state.adding and not self.table.is_available:
            raise ValidationError(
                f'Столик №{self.table.number} сейчас недоступен.'
            )

        # Проверяем прошедшие дату и время только
        # при создании новой брони.
        if self._state.adding and self.date and self.time:

            reservation_datetime = timezone.make_aware(
                datetime.combine(
                    self.date,
                    self.time
                )
            )

            if reservation_datetime < timezone.now():
                raise ValidationError(
                    'Нельзя создать бронирование '
                    'на прошедшие дату и время.'
                )

        # Количество гостей всегда должно соответствовать
        # вместимости столика.
        if self.guests > self.table.seats:
            raise ValidationError(
                f'За столиком только '
                f'{self.table.seats} мест.'
            )

        # Проверяем занятость столика.
        conflict = Reservation.objects.filter(
            table=self.table,
            date=self.date,
            time=self.time,
            status__in=[
                self.Status.PENDING,
                self.Status.CONFIRMED,
            ]
        ).exclude(
            pk=self.pk
        )

        if conflict.exists():
            raise ValidationError(
                'Этот столик уже забронирован '
                'на выбранное время.'
            )

    def save(self, *args, **kwargs):

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f'Бронь №{self.id} — '
            f'столик №{self.table.number}'
        )