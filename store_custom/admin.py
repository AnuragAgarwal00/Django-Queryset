from django.contrib import admin
from django.contrib.contenttypes.admin import GenericStackedInline, GenericTabularInline


from store.admin import ProductAdmin
from store.models import Product
from tags.models import TaggedItem


# Here in the admin module of the store app, we are importing TaggedItem from the tag app
# so that means our store app has a dependency to our tag app
# so we cannot build & deploy it independently
# Ideally our apps should be self contained so we can easily plug them into new projects
# so here we need to decouple the store app from tag app
# But how?
# so here are tag & store app, we want to build and deploy them independently of each other
# So none of these apps should know nothing about each other
# In this project we will create a new app named as store_custom
# And this is the customization of the store app which knows about both these apps [tags, store]
# This is very specific to our project
# Slo we are not going to deploy this app for others to reuse
# TaggedItem SHOULD BE MOVED TO STORE_CUSTOM APP BECZ THATS WHERE WE ARE REFRENCING TAGGEDiTEM CLASS
# NOW WE NEED TO CREATE A NEW PRODUCT ADMIN CLASS WITH EXTENDS ProductAdmin FROM STORE.ADMIN APP

class TagInline(GenericTabularInline):
    autocomplete_fields = ['tag']
    model = TaggedItem


class CustomProductAdmin(ProductAdmin):
    inlines = [TagInline]

# so now we have a new productdmin class
# we need to unregister the old one & register the new one
admin.site.unregister(Product)
admin.site.register(Product, CustomProductAdmin)