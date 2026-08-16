import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from menu.models import Product


class Order(models.Model):

    class Status(models.TextChoices):
        NEW = 'new', 'Новый'
        CONFIRMED = 'confirmed', 'Подтверждён'
        PREPARING = 'preparing', 'Готовится'
        READY = 'ready', 'Готов'
        COMPLETED = 'completed', 'Завершён'
        CANCELLED = 'cancelled', 'Отменён'

    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='orders'
    )

    checkout_token = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False
)

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.NEW
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    @property
    def total(self):
        return sum(
            item.subtotal
            for item in self.items.all()
        )

    def __str__(self):
        return f'Заказ №{self.id}'


class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
        related_name='order_items'
    )

    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    class Meta:
        verbose_name = 'Позиция заказа'
        verbose_name_plural = 'Позиции заказа'

        constraints = [
            models.UniqueConstraint(
                fields=['order', 'product'],
                name='unique_product_per_order',
            ),
        ]

    def clean(self):
        if (
            self._state.adding
            and self.product_id
            and not self.product.is_available
        ):
            raise ValidationError(
                f'Товар "{self.product.name}" сейчас недоступен.'
            )

    def save(self, *args, **kwargs):

        # Цена фиксируется только при создании OrderItem.
        if self._state.adding and self.product_id:
            self.price = self.product.price

        self.full_clean()

        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.product.name} × {self.quantity}'

    @property
    def subtotal(self):

        if (
            not self.product_id
            or not self.quantity
            or self.price is None
        ):
            return 0

        return self.price * self.quantity

