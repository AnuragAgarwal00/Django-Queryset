from django.contrib import admin
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse


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

@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """SOMETIMES WE NEED TO OVERRIDE THE BASE QUERYSET USED  FOR RENDERING A LIST PAGE
    EG => IN LIST OF COLLECTION, YOU NEED TO ADD A COLUMN TO SHOW NO. OF PRODUCTS IN EACH COLLECTION"""
    list_display = ['title', 'product_count']

    @admin.display(ordering='products_count')
    def product_count(self, collection):
        # HOW TO ADD LINKS?
        # WHEN WE CLIK ON THIS LINK, WE CAN SEE THE PRODUCTS IN EACH COLLECTION
        # INSTAED OF RETURNING A NO. WE SHOULD RETURN A STRING CONTAINING AN HTML LINK
        # TO GENERATE AN HTML LINK WE SHOULD IMPORT A UTILITY FUNCTIONS ON THE TOP format_html
        # HOW TO SEND OUR USERS TO THE PRODUCT PAGE?
        # IN PRODUCT PAGE JUST LOOK AT THE URL admin/store/product
        # WE DON'T WANT TO HARD CODE THIS URL INTO OUR CODE BECZ THIS URL CAN CHANGE IN THE FUTURE
        # SO WE SHOULD SHOULD ASK DJANGO TO GIVE US THE URL OF THIS PAGE AND TO DO THAT WE HAVE TO
        # IMPORT ANOTHER UTILITY FUNCTION ON TOP - reverse
        # HERE YOU WILL CALL THE REVERSE FUNCTION AND GIVE IT A SPECIAL AGRUMENT
        # reverse('admin:AppName_Model_page')
        # what app are we working on => Store App
        # what is the target model?
        # IT'S THE PRODUCT MODEL BECZ WE WANT TO SEND THE USERS TO THE PRODUCT LIST PAGE
        # WHAT IS THE TARGET PAGE?
        # ITS CALLED "changelist" (list of products is called changelist)
        # we GO TO THE LIST OF PRODUCTS BUT THERE IS NO FILTERS APPLIED ON PRODUCT PAGE?
        # TO APPLY A FILTER WE NEED TO APPEND A QUERYSTRING TO THE URL 
        # SO WE TYPE  ?Collection_id=1, so we need to add this part dynamically
        # ? represents the begining of the querystring
        # for LONG STRING PLZ PERFER WRAPPING THE STATEMENTS INSIDE PARENTHESIS
        # for genrating string we use urlencode function
        # we call urlencode func and give it a dictionary becz a querystring can contain multiple key-value pairs
        # thats why we use a dictionary here
        url = (
            reverse('admin:store_product_changelist') + 
            '?' + 
            urlencode({
                'collection_id': str(collection.id)
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count)

    def get_queryset(self, request):
        """EVERY MODEL ADMIN HAS A METHOD CALLED GETQUERYSET WHICH YOU CAN OVERRIDE"""
        return super(CollectionAdmin, self).get_queryset(request).annotate(
            products_count=Count('product')
        )
    
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'placed_at', 'payment_status', 'customer', 'customer_membership']
    list_select_related = ['customer']
    ordering = ['placed_at']
    list_per_page = 10

    def customer_membership(self, order):
        return order.customer.membership
