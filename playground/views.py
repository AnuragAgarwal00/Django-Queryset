from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from store.models import Product, OrderItem

def sorting(request):
    # Sorting
    # We can sort by multiple fields - sort by unit_price in asc order & title in desc order
    # with this implimentation we gonna sort our product to cheapest to most expensive
    # order by returns queryset and one of the method is reverse
    # this will reverse the direct of sorting
    # unit price will be sorted in desc and title in asc
    queryset = Product.objects.order_by('unit_price', '-title').reverse()
    queryset = Product.objects.filter(collection__id=1).order_by('unit_price')

    # Sometimes we wanna sort the result & pick only the first value
    # with this you are not getting queryset
    # The moment you access the element the queryset gets evaluated & returns the object
    product = Product.objects.order_by('unit_price')[0]

    # Another Way to re-write the same query
    # Sort the products in asc & give me the 1st object
    # earliest methods returns an object
    product = Product.objects.earliest('unit_price')

    # Latest sorts the products in desc order and returns the 1st object
    product = Product.objects.latest('unit_price')

    return render(request, 'hello.html', {'name': 'Anurag', 'products': list(queryset)})

def selecting_fields_to_query(request):
    # when you query objects by defaults all fields are read from db
    # what if u r interested only in specific fields
    # we have an inner join between product & collection table
    # values method returns dictionary obj
    queryset = Product.objects.values('id', 'title', 'collection__title')

    # we have another method called values list
    # This method returnd tuples instead of dictionary
    # each object will be a tuple of 3 values
    queryset = Product.objects.values_list('id', 'title', 'collection__title')

def exercise_one(request):
    """Write a queryto select products that have been ordered
    & Sort them by title"""
    queryset = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    return render(request, 'hello.html', {'products': queryset})

def deferring_fields(request):
    # with only we can specifiy the fields we want to read from the db
    # How only is different from values method?
    # with only method, you get instance of product class
    # with values method you get dictionary objects
    # Be careful while using the only method else you gonna end up sending extra query to db
    queryset = Product.objects.only('id', 'title')

    # We have another method that is opposite of only => defer
    # with this method we csn defer loading of certain fields
    # eg => we are interested in all the fields except description field
    # Be careful while using the only method else you gonna end up sending extra query to db
    queryset = Product.objects.defer('description')

    return render(request, 'hello.html', {'products': queryset})








