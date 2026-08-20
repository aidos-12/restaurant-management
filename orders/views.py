from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render

from users.decorators import employee_required

from .models import Order
from .services import change_order_status


@employee_required
def order_list(request):

    status = request.GET.get('status')

    orders = Order.objects.select_related(
        'customer'
    ).prefetch_related(
        'items__product'
    )

    if status:
        orders = orders.filter(
            status=status
        )

    new_orders_count = Order.objects.filter(
        status=Order.Status.NEW
    ).count()

    preparing_orders_count = Order.objects.filter(
        status=Order.Status.PREPARING
    ).count()

    ready_orders_count = Order.objects.filter(
        status=Order.Status.READY
    ).count()

    return render(
        request,
        'orders/order_list.html',
        {
            'orders': orders,
            'current_status': status,
            'status_choices': Order.Status.choices,
            'new_orders_count': new_orders_count,
            'preparing_orders_count': preparing_orders_count,
            'ready_orders_count': ready_orders_count,
        }
    )


@employee_required
def order_detail(request, order_id):

    order = get_object_or_404(
        Order.objects.select_related(
            'customer'
        ).prefetch_related(
            'items__product'
        ),
        id=order_id
    )

    return render(
        request,
        'orders/order_detail.html',
        {
            'order': order,
        }
    )


@employee_required
def update_order_status(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id
    )

    if request.method == 'POST':

        new_status = request.POST.get('status')

        try:
            change_order_status(
                order,
                new_status
            )

        except ValidationError as error:

            return render(
                request,
                'orders/access_denied.html',
                {
                    'error': error.message,
                },
                status=400
            )

    return redirect(
        'employee_order_detail',
        order_id=order.id
    )