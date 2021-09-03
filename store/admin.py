from django.contrib import admin

from .models import Collection, Product, Customer, Order

#register your model here

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    # show 10 product per page
    list_per_page = 10
    list_select_related = ['collection']
    # for complete list of customization just google DjangoModelAdmin

    # ADDING COMPUTED COULMN TO THE LIST OF PRODUCT
    # ADD A NEW COULN CALLED INVENTORY STATUS IF THE INVENTORY OF PRODUCT < 10-
    # HERE WE SEE LOW ELSE WE SEE OK

    # SO WE WANNA TAKE A PRODUCT AND DEPENDING UPON ITS INVENTORY, WE WILL RETURN
    # ITS INVENTORY STATUS
    # To implement SORTING YOU NEED TO APPLY @ADMIN.DISPLAY DECORATOR()
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'Low'
        return 'Ok'

    # WHAT IF WE DON'T WANT TO SHOW THE STRING REPRESENTATION OF A COLLECTION.
    # WHAT IF WE WANT TO SHOW A PARTICULAR FIELD IN COLLECTION MODEL?
    # IMAGINE WE HAVE A SPECIAL FIELD IN COLLECTION TABLE  CALLED 'TITLE' YOU WANTS TO SHOW ON PRODUCT PAGE
    def collection_title(self, product):
        return product.collection.title



@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 10

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['placed_at', 'payment_status', 'customer', 'customer_membership']
    list_select_related = ['customer']
    ordering = ['placed_at']
    list_per_page = 10

    def customer_membership(self, order):
        return order.customer.membership
admin.site.register(Collection)
