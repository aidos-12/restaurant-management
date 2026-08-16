from django.urls import path

from .views import (
    menu,
    add_to_cart,
    cart,
    remove_from_cart,
    increase_quantity,
    decrease_quantity,
    clear_cart,
    checkout,
    order_success,
)


urlpatterns = [

    path(
        'menu/',
        menu,
        name='menu'
    ),

    path(
        'cart/',
        cart,
        name='cart'
    ),

    path(
        'cart/add/<int:product_id>/',
        add_to_cart,
        name='add_to_cart'
    ),

    path(
        'cart/remove/<int:product_id>/',
        remove_from_cart,
        name='remove_from_cart'
    ),

    path(
        'cart/increase/<int:product_id>/',
        increase_quantity,
        name='increase_quantity'
    ),

    path(
        'cart/decrease/<int:product_id>/',
        decrease_quantity,
        name='decrease_quantity'
    ),

    path(
        'cart/clear/',
        clear_cart,
        name='clear_cart'
    ),

    path(
        'checkout/',
        checkout,
        name='checkout'
    ),

    path(
        'order/<int:order_id>/success/',
        order_success,
        name='order_success'
    ),
]