from django.urls import path

from .views import (
    order_list,
    order_detail,
    update_order_status,
)


urlpatterns = [

    path(
        '',
        order_list,
        name='employee_orders'
    ),

    path(
        '<int:order_id>/',
        order_detail,
        name='employee_order_detail'
    ),

    path(
        '<int:order_id>/status/',
        update_order_status,
        name='update_order_status'
    ),
]