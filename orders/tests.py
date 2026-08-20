from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from menu.models import Category, Product

from .models import Order, OrderItem


User = get_user_model()


class OrderModelTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='test_client',
            password='test_password123'
        )

        self.category = Category.objects.create(
            name='Тестовая категория'
        )

        self.product = Product.objects.create(
            category=self.category,
            name='Тестовое блюдо',
            description='Тестовое описание',
            price=Decimal('2500.00'),
            is_available=True
        )

    def test_order_created_successfully(self):

        order = Order.objects.create(
            customer=self.user
        )

        self.assertEqual(
            order.customer,
            self.user
        )

        self.assertEqual(
            order.status,
            Order.Status.NEW
        )

        self.assertIsNotNone(
            order.checkout_token
        )

    def test_checkout_token_is_unique(self):

        order_1 = Order.objects.create(
            customer=self.user
        )

        order_2 = Order.objects.create(
            customer=self.user
        )

        self.assertNotEqual(
            order_1.checkout_token,
            order_2.checkout_token
        )

    def test_order_item_saves_product_price(self):

        order = Order.objects.create(
            customer=self.user
        )

        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal('1.00')
        )

        self.assertEqual(
            item.price,
            self.product.price
        )

    def test_order_item_subtotal(self):

        order = Order.objects.create(
            customer=self.user
        )

        item = OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=3,
            price=Decimal('1.00')
        )

        self.assertEqual(
            item.subtotal,
            Decimal('7500.00')
        )

    def test_order_total(self):

        order = Order.objects.create(
            customer=self.user
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=2,
            price=Decimal('1.00')
        )

        self.assertEqual(
            order.total,
            Decimal('5000.00')
        )

    def test_unavailable_product_cannot_be_added_to_order(self):

        self.product.is_available = False
        self.product.save()

        order = Order.objects.create(
            customer=self.user
        )

        item = OrderItem(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_order_item_quantity_must_be_positive(self):

        order = Order.objects.create(
            customer=self.user
        )

        item = OrderItem(
            order=order,
            product=self.product,
            quantity=0,
            price=self.product.price
        )

        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_same_product_cannot_be_added_twice(self):

        order = Order.objects.create(
            customer=self.user
        )

        OrderItem.objects.create(
            order=order,
            product=self.product,
            quantity=1,
            price=self.product.price
        )

        duplicate_item = OrderItem(
            order=order,
            product=self.product,
            quantity=2,
            price=self.product.price
        )

        with self.assertRaises(ValidationError):
            duplicate_item.validate_constraints(
                exclude=None
            )


class OrderViewTests(TestCase):

    def setUp(self):

        self.user = User.objects.create_user(
            username='test_client',
            password='test_password123'
        )

        self.employee = User.objects.create_user(
            username='test_employee',
            password='test_password123'
        )

        from django.contrib.auth.models import Group

        employee_group = Group.objects.create(
            name='Сотрудник'
        )

        self.employee.groups.add(
            employee_group
        )

    def test_order_list_requires_employee(self):

        response = self.client.get(
            reverse('employee_orders')
        )

        self.assertEqual(
            response.status_code,
            302
        )

    def test_order_list_denies_regular_user(self):

        self.client.login(
            username='test_client',
            password='test_password123'
        )

        response = self.client.get(
            reverse('employee_orders')
        )

        self.assertEqual(
            response.status_code,
            403
        )

    def test_order_list_allows_employee(self):

        self.client.login(
            username='test_employee',
            password='test_password123'
        )

        response = self.client.get(
            reverse('employee_orders')
        )

        self.assertEqual(
            response.status_code,
            200
        )