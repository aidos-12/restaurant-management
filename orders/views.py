from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Order


def employee_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):

        if not request.user.groups.filter(
            name='Сотрудник'
        ).exists():
            return render(
                request,
                'orders/access_denied.html',
                status=403
            )

        return view_func(request, *args, **kwargs)

    return wrapper


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

            'preparing_orders_count':
                preparing_orders_count,

            'ready_orders_count':
                ready_orders_count,
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

        valid_statuses = dict(
            Order.Status.choices
        )

        if new_status in valid_statuses:

            allowed_transitions = {
                Order.Status.NEW: [
                    Order.Status.CONFIRMED,
                    Order.Status.CANCELLED,
                ],

                Order.Status.CONFIRMED: [
                    Order.Status.PREPARING,
                    Order.Status.CANCELLED,
                ],

                Order.Status.PREPARING: [
                    Order.Status.READY,
                    Order.Status.CANCELLED,
                ],

                Order.Status.READY: [
                    Order.Status.COMPLETED,
                ],

                Order.Status.COMPLETED: [],

                Order.Status.CANCELLED: [],
            }

            if new_status not in allowed_transitions.get(
                order.status,
                []
            ):
                return render(
                    request,
                    'orders/access_denied.html',
                    {
                        'error':
                            'Недопустимый переход статуса.'
                    },
                    status=400
                )

            order.status = new_status
            order.save()

    return redirect(
        'employee_order_detail',
        order_id=order.id
    )