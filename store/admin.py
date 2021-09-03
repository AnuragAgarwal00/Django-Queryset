from django.contrib import admin

from .models import Collection, Product, Customer

#register your model here

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status']
    list_editable = ['unit_price']
    # show 10 product per page
    list_per_page = 10
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

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership']
    list_editable = ['membership']
    ordering = ['first_name', 'last_name']
    list_per_page = 10
admin.site.register(Collection)
