from django.core.exceptions import ValidationError
from .models import Order


ALLOWED_STATUS_TRANSITIONS = {
    Order.Status.NEW: [Order.Status.CONFIRMED,Order.Status.CANCELLED,],

    Order.Status.CONFIRMED: [Order.Status.PREPARING,Order.Status.CANCELLED,],

    Order.Status.PREPARING: [Order.Status.READY,Order.Status.CANCELLED,],

    Order.Status.READY: [Order.Status.COMPLETED,],

    Order.Status.COMPLETED: [],

    Order.Status.CANCELLED: [],}


def change_order_status(order, new_status):
    valid_statuses = dict(Order.Status.choices)

    if new_status not in valid_statuses:
        raise ValidationError('Недопустимый статус заказа.')

    allowed_statuses = ALLOWED_STATUS_TRANSITIONS.get(order.status,[])

    if new_status not in allowed_statuses:
        raise ValidationError('Недопустимый переход статуса заказа.')

    order.status = new_status
    order.save(update_fields=['status','updated_at',])
    return order