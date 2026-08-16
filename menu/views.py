from django.shortcuts import render

from .models import Category


def home(request):
    return render(request, 'menu/home.html')


def menu(request):
    categories = Category.objects.prefetch_related('products')

    return render(
        request,
        'menu/menu.html',
        {'categories': categories}
    )