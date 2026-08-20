from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse

from orders.models import Order
from reservations.models import Reservation


User = get_user_model()


class UserModelTests(TestCase):

    def test_user_can_be_created(self):

        user = User.objects.create_user(
            username='test_user',
            password='test_password123'
        )

        self.assertEqual(
            user.username,
            'test_user'
        )

        self.assertTrue(
            user.check_password('test_password123')
        )

    def test_user_password_is_hashed(self):

        user = User.objects.create_user(
            username='test_user',
            password='test_password123'
        )

        self.assertNotEqual(
            user.password,
            'test_password123'
        )


class AuthenticationTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='test_user',
            password='test_password123'
        )

    def test_login_successful(self):

        response = self.client.post(
            reverse('login'),
            {
                'username': 'test_user',
                'password': 'test_password123',
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertTrue(
            response.wsgi_request.user.is_authenticated
        )

    def test_login_with_wrong_password_fails(self):

        response = self.client.post(
            reverse('login'),
            {
                'username': 'test_user',
                'password': 'wrong_password',
            }
        )

        self.assertEqual(
            response.status_code,
            200
        )

        self.assertFalse(
            response.wsgi_request.user.is_authenticated
        )

    def test_logout(self):

        self.client.login(
            username='test_user',
            password='test_password123'
        )

        response = self.client.get(
            reverse('logout')
        )

        self.assertEqual(
            response.status_code,
            302
        )


class RegistrationTests(TestCase):

    def test_registration_creates_client_user(self):

        response = self.client.post(
            reverse('register'),
            {
                'username': 'new_user',
                'password1': 'StrongPassword123!',
                'password2': 'StrongPassword123!',
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        user = User.objects.get(
            username='new_user'
        )

        self.assertTrue(
            user.groups.filter(
                name='Клиент'
            ).exists()
        )

        self.assertTrue(
            user.check_password(
                'StrongPassword123!'
            )
        )


class PermissionTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='test_user',
            password='test_password123'
        )

    def test_profile_requires_login(self):

        response = self.client.get(
            reverse('profile')
        )

        self.assertEqual(
            response.status_code,
            302
        )

    def test_order_history_requires_login(self):

        response = self.client.get(
            reverse('order_history')
        )

        self.assertEqual(
            response.status_code,
            302
        )

    def test_authenticated_user_can_open_profile(self):

        self.client.login(
            username='test_user',
            password='test_password123'
        )

        response = self.client.get(
            reverse('profile')
        )

        self.assertEqual(
            response.status_code,
            200
        )

    def test_authenticated_user_can_open_order_history(self):

        self.client.login(
            username='test_user',
            password='test_password123'
        )

        response = self.client.get(
            reverse('order_history')
        )

        self.assertEqual(
            response.status_code,
            200
        )


class EmployeeTests(TestCase):

    def setUp(self):

        self.employee = User.objects.create_user(
            username='employee',
            password='test_password123'
        )

        self.employee_group = Group.objects.create(
            name='Сотрудник'
        )

        self.employee.groups.add(
            self.employee_group
        )

    def test_employee_belongs_to_employee_group(self):

        self.assertTrue(
            self.employee.groups.filter(
                name='Сотрудник'
            ).exists()
        )

    def test_employee_is_redirected_to_employee_orders_after_login(self):

        response = self.client.post(
            reverse('login'),
            {
                'username': 'employee',
                'password': 'test_password123',
            }
        )

        self.assertEqual(
            response.status_code,
            302
        )

        self.assertEqual(
            response.url,
            reverse('employee_orders')
        )