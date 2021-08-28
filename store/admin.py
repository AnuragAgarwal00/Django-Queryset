from django.contrib import admin, messages
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.db.models.query import QuerySet
from django.urls import reverse

from . import models

INVENTORY_LOW = '<10'
INVENTORY_MID = '10<50'
INVENTORY_HIGH = '50<100'

class InventoryFilter(admin.SimpleListFilter):
    title = 'Inventory'
    parameter_name = 'inventory'
  

    def lookups(self, request, model_admin):
        return [
            (INVENTORY_LOW, 'Low'),
            (INVENTORY_MID, 'Mid'),
            (INVENTORY_MID, 'High'),


        ]

    def queryset(self, request, queryset: QuerySet):
        if self.value() == INVENTORY_LOW:
            return queryset.filter(inventory__lt=10)
        elif self.value() == INVENTORY_MID:
            return queryset.filter(inventory__lt=50, inventory__gt=10)
        else:
            return queryset.filter(inventory__lte=100, inventory__gt=50)




@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price',]
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_select_related = ['collection']
    list_per_page = 10

    def collection_title(self, product):
        return product.collection.title

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        status = " "
        if product.inventory < 10:
            status = "Low"
            return status
        status = "Ok"
        return status

    @admin.action(description="Clear Inventory")
    def clear_inventory(self, request, queryset):
        print('queryset', queryset)
        updated_count = queryset.update(inventory=0)
        print('updated_count', updated_count)
        self.message_user(
            request,
            f'{updated_count} products were successfully updated!',
            messages.ERROR)


@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'no_of_orders']
    list_editable = ['membership']
    list_per_page = 10
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='no_of_orders')
    def no_of_orders(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({
                'customer__id': str(customer.id)
            })
            )
        return format_html('<a href="{}">{}</a>', url, customer.no_of_orders)

    def get_queryset(self, request):
        return super(CustomerAdmin, self).get_queryset(request).annotate(
            no_of_orders=Count('order')
        )

@admin.register(models.Order)
class orderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'payment_status', 'customer_name']
    list_editable = ['payment_status',]
    list_per_page = 10
    list_select_related = ['customer']

    @admin.display(ordering='customer')
    def customer_name(self, order):
        return f"{order.customer.first_name} {order.customer.last_name}"

    
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        # reverse(admin:app_model_page)
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
                'collection__id': str(collection.id)
            })
            )

        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        return super(CollectionAdmin, self).get_queryset(request).annotate(
            products_count=Count('product')
        )



