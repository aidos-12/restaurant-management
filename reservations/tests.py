from datetime import date, time, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Reservation, Table


User = get_user_model()


class ReservationModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_client',
            password='test_password123'
        )

        self.table = Table.objects.create(
            number=1,
            seats=4,
            is_available=True
        )

    def test_reservation_created_successfully(self):
        reservation = Reservation.objects.create(
            customer=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=2,
            comment='Тестовая бронь'
        )

        self.assertEqual(
            reservation.customer,
            self.user
        )

        self.assertEqual(
            reservation.table,
            self.table
        )

        self.assertEqual(
            reservation.guests,
            2
        )

        self.assertEqual(
            reservation.status,
            Reservation.Status.PENDING
        )

    def test_cannot_book_more_guests_than_table_seats(self):
        reservation = Reservation(
            customer=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=5
        )

        with self.assertRaises(Exception):
            reservation.full_clean()

    def test_cannot_create_duplicate_reservation(self):
        reservation = Reservation.objects.create(
            customer=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=2
        )

        duplicate = Reservation(
            customer=self.user,
            table=self.table,
            date=reservation.date,
            time=reservation.time,
            guests=2
        )

        with self.assertRaises(Exception):
            duplicate.full_clean()

    def test_cannot_book_unavailable_table(self):
        self.table.is_available = False
        self.table.save()

        reservation = Reservation(
            customer=self.user,
            table=self.table,
            date=date.today() + timedelta(days=1),
            time=time(19, 0),
            guests=2
        )

        with self.assertRaises(Exception):
            reservation.full_clean()


class ReservationViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_client',
            password='test_password123'
        )

        self.table = Table.objects.create(
            number=1,
            seats=4,
            is_available=True
        )

    def test_reservation_create_requires_login(self):
        response = self.client.get(
            reverse(
                'reservation_create',
                args=[self.table.id]
            )
        )

        self.assertEqual(
            response.status_code,
            302
        )

    def test_tables_page_is_available(self):
        response = self.client.get(
            reverse('tables')
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_logged_in_user_can_open_booking_page(self):
        self.client.login(
            username='test_client',
            password='test_password123'
        )

        response = self.client.get(
            reverse(
                'reservation_create',
                args=[self.table.id]
            )
        )

        self.assertEqual(
            response.status_code,
            200
        )