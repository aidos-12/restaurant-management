from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from menu.models import Category, Product
from orders.models import Order, OrderItem


def menu(request):

    categories = Category.objects.prefetch_related(
        'products'
    )

    return render(
        request,
        'shop/menu.html',
        {
            'categories': categories,
        }
    )


def add_to_cart(request, product_id):

    if request.method != 'POST':
        return redirect('menu')

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    cart = request.session.get('cart', {})

    product_id = str(product.id)

    quantity = cart.get(product_id, 0)

    if not isinstance(quantity, int) or quantity < 0:
        quantity = 0

    cart[product_id] = quantity + 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('menu')


def cart(request):

    cart_data = request.session.get(
        'cart',
        {}
    )

    products = Product.objects.filter(
        id__in=cart_data.keys(),
        is_available=True
    )

    cart_items = []

    for product in products:

        quantity = cart_data.get(
            str(product.id),
            0
        )

        if not isinstance(quantity, int) or quantity <= 0:
            continue

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': product.price * quantity,
        })

    total = sum(
        item['subtotal']
        for item in cart_items
    )

    return render(
        request,
        'shop/cart.html',
        {
            'cart_items': cart_items,
            'total': total,
        }
    )


def remove_from_cart(request, product_id):

    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get(
        'cart',
        {}
    )

    product_id = str(product_id)

    cart.pop(product_id, None)

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def increase_quantity(request, product_id):

    if request.method != 'POST':
        return redirect('cart')

    product = get_object_or_404(
        Product,
        id=product_id,
        is_available=True
    )

    cart = request.session.get(
        'cart',
        {}
    )

    product_id = str(product.id)

    quantity = cart.get(product_id, 0)

    if not isinstance(quantity, int) or quantity < 0:
        quantity = 0

    cart[product_id] = quantity + 1

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def decrease_quantity(request, product_id):

    if request.method != 'POST':
        return redirect('cart')

    cart = request.session.get(
        'cart',
        {}
    )

    product_id = str(product_id)

    if product_id in cart:

        quantity = cart[product_id]

        if not isinstance(quantity, int):
            quantity = 1

        quantity -= 1

        if quantity <= 0:
            del cart[product_id]
        else:
            cart[product_id] = quantity

    request.session['cart'] = cart
    request.session.modified = True

    return redirect('cart')


def clear_cart(request):

    if request.method != 'POST':
        return redirect('cart')

    request.session['cart'] = {}
    request.session.modified = True

    return redirect('cart')


@login_required
def checkout(request):

    cart_data = request.session.get(
        'cart',
        {}
    )

    if not cart_data:
        return redirect('cart')

    product_ids = list(cart_data.keys())

    products = Product.objects.filter(
        id__in=product_ids
    )

    products_by_id = {
        str(product.id): product
        for product in products
    }

    cart_items = []

    for product_id in product_ids:

        product = products_by_id.get(product_id)
        quantity = cart_data.get(product_id)

        if product is None:
            return render(
                request,
                'shop/checkout.html',
                {
                    'error':
                        'Один из товаров больше не существует.',
                }
            )

        if not product.is_available:
            return render(
                request,
                'shop/checkout.html',
                {
                    'error':
                        f'Товар "{product.name}" '
                        'сейчас недоступен.',
                }
            )

        if (
            not isinstance(quantity, int)
            or quantity <= 0
        ):
            return render(
                request,
                'shop/checkout.html',
                {
                    'error':
                        'Некорректное количество товара.',
                }
            )

        subtotal = product.price * quantity

        cart_items.append({
            'product': product,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    total = sum(
        item['subtotal']
        for item in cart_items
    )

    if request.method == 'POST':

        with transaction.atomic():

            order = Order.objects.create(
                customer=request.user
            )

            for item in cart_items:

                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['product'].price
                )

        request.session['cart'] = {}
        request.session.modified = True

        return redirect(
            'order_success',
            order_id=order.id
        )

    return render(
        request,
        'shop/checkout.html',
        {
            'cart_items': cart_items,
            'total': total,
        }
    )


@login_required
def order_success(request, order_id):

    order = get_object_or_404(
        Order,
        id=order_id,
        customer=request.user
    )

    return render(
        request,
        'shop/order_success.html',
        {
            'order': order,
        }
    )