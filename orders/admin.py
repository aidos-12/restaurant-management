from django.contrib import admin
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from .models import Order, OrderItem

class OrderItemInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        has_items = False
        for form in self.forms:
            if not form.cleaned_data:
                continue
            if form.cleaned_data.get('DELETE'):
                continue
            if form.cleaned_data.get('product'):
                has_items = True
                break
        if not has_items:
            raise ValidationError('Заказ должен содержать хотя бы один товар.')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1
    readonly_fields = ('price', 'subtotal')
    formset = OrderItemInlineFormSet


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'customer',
        'status',
        'total',
        'created_at',
        'updated_at',
    )

    list_filter = ('status','created_at',)
    readonly_fields = ('total',)
    search_fields = ('customer__username','customer__email',)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = (
        'order',
        'product',
        'quantity',
        'price',
        'subtotal',
    )

    list_filter = ('product__category',)

    search_fields = ('product__name',)

    readonly_fields = ('price', 'subtotal')

