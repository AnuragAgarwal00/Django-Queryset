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
