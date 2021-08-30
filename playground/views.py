from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q, Value, F, Func, ExpressionWrapper
from django.db.models.aggregates import Min, Max, Avg, Count, Sum
from django.db.models.functions import Concat
from django.contrib.contenttypes.models import ContentType

from store.models import Product, OrderItem, Order, Customer
from tag.models import TaggedItem

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

def selecting_realted_objects(request):
    # when we ask for products django will only query the product table not foreign key or M2M
    # It's not going to query the related table unless you specifically instruct it to do it so
    queryset = Product.objects.all()

    # Here we want to pre-load products with their collection
    # when we use select related method django will create join between our tables
    # we use select related when the end of relation has one instance
    # eg => A product has one collection
    queryset = Product.objects.select_related('collection').all()

    # We have another method called prefetch related
    # we use prefetch related when the other end of relationship has many objects
    # eg => each product can have multiple promotions
    # to pre-load the promotions we use prefetch related
    # We gave 2 seperate query in db for products &b other inner join for promotions
    # Django reads these sets & popultates in memory
    queryset = Product.objects.prefetch_related('promotions').all()

    # we can also combine these 2 methods
    # eg => you wnats to know All the products with their promotions & collection
    # both these methods returns a queryset and thats why we can chain these methods after one other
    # order of these methods doesn't matter
    queryset = Product.objects.select_related('collection').prefetch_related('promotions').all()

    return render(request, 'hello.html', {'products': queryset})


def exercise_two(request):
    """Get the last 5 orders with their Customer and items including the product refrencing"""
    queryset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product') .order_by('-placed_at')[:5]

    return render(request, 'hello.html', {'products': queryset})

def aggregating_Objects(request):
    """Sometimes u wants to compute summaries like Max or Avg price of our products.
    This is where we use Aggregate method."""

    # Let's say we wants to count our products
    # the proper way to count the no. of products is to use id or the primary_key
    # The Aggregate method doesn't returns a queryset becz when we calculate the summary of value it really doesnt make any sense to do extra with it
    # Here aggregate method returns a dictionarey obj
    # Result => {'id__count': 1000} bcz we used id column for counting obj
    result = Product.objects.aggregate(Count('id'))

    # we can easily change the name of the key
    result = Product.objects.aggregate(count=Count('id'))

    # we can also calcuate min price
    result = Product.objects.aggregate(count=Count('id'), min_price=Min('unit_price'))

    # Since aggregate is one of the method of queryset, we can apply wherever we have a queryset
    result = Product.objects.filter(collection__id=1).aggregate(count=Count('id'), max_price=Max('unit_price'))

    return render(request, 'hello.html', {'products': queryset})

def annotating_objects(request):
    """ Sometimes you wanna add additional attributes to your objects while quering them.
    This is where we use the annotate method.
    Expressions Class in annoting objects:
    Values : number, boolean, string
    F : Using F class you can refrence field in the same or other tables
    Func : for calling database functions
    Aggregate: Max, Sum, Min, Count """

    # Let's say while querying customers, you want to give every customer a new fields called "is_new= True"
    queryset =  Customer.objects.annotate(is_new=Value(True))

    # This time we wanna give customer a new field called new_id
    queryset = Customer.objects.annotate(new_id=F('id'))

    # We can also perform computations here
    # Eg => we can add 1 to id to generate new id
    queryset = Customer.objects.annotate(new_id=F('id') + 1)

    return render(request, 'hello.html', {'result': queryset})

def calling_database_functions(request):
    # we gonna give our customers a new field full_name
    # This is where we gonna call concat func of a database engine
    # Conact
    full_name = Customer.objects.annotate(
        full_name=Func(F('first_name'), 
        Value(" "), 
        F('last_name'), 
        function="CONCAT"
        ))

    # There is also a shortcut to achieve the same results
    # for space u need to wrap inside Value class becz django think " " is a column in our table
    full_name = Customer.objects.annoate(Concat('first_name', Value(" "), 'last_name'))

    # Just google django databse functions for exploring more

    return render(request, 'hello.html', {'full_name': full_name})

def grouping_data(request):
    # Let's say we want to see no. of orders each customers has placed
    # for reverse relationship we cannot use order_Set to count no. of orders
    # In db we are selecting * from customer table & we are counting no. of orders
    # & we have a left join between orders & customers table becz not every customer has a order
    # finally we have group clause for grouping no of orders for each customer

    queryset = Customer.objects.annotate(orders_count=Count('order'))

    return render(request, 'hello.html', {'result': queryset})

def working_with_epression_wrapper(request):
    """Another derivate of expression class called ExpressionWrapper.
    We use this class when building complex expressions."""

    # Let's say we gonna annoate our products and give them a new field called discounted_price
    If you run this query, you gonna get an exception
    # Expression contains mixed types DecimalField, FloatField. You must set the output field
    queryset = Product.objects.annotate(discounted_price=F('unit_price') * 0.8)

    # To solve the above problem
    discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    queryset = Product.objects.annotate(discounted_price=discounted_price)

    return render(request, 'hello.html', {'result': queryset})
    
def querying_generic_relationship(request):
    """How to find tags for a given product?"""
    # in database table => django_content_type, you can see all the models in our app 
    # To find the tags of a given product, 1st we have to find the content-type id of the product model
    # In databse the contenttype of Product model is 11, so once we find this, then we can go to the table TaggedItem & write a qauery to filter all records -
    # where contenttype id equals 11 and object_id equaLS id of the product, whose tags we wanna find out

    # 1st we need to find the contenttype id   for the product model
    # in tagged_item table we have a field called tag_id, which is ForeignKey to Tag class
    # the actuakl tag in not storef in tagged_item table it is stored in tags_tag
    # so we need to pre-load  tag_id field because we will end up sending extra query to db

    content_type = ContentType.objects.get_for_model(Product)
    queryset = TaggedItem.objects \
        .select_related('tag') \
        .filter(
            content_type=content_type,
            object_id=1
    )
    # we have 2 query
    # 1st query  id for finding contenttype of product model
    # 2nd query  is for reading tags 4 given product

    return render(request, 'hello.html', {'result': list(queryset)})

def custom_manager(request):
    queryset = TaggedItem.objects.get_tags_for(obj_type=Product, obj_id=1)

    return render(request, 'hello.html', {'result': list(queryset)})

def understanding_queryset_cache(request):
    """Caching Mechanism built into queryset"""
    # when we convert this queryset into list, django is gonna evalute this queryset & that's when it's go into db to get the results
    # This is an expensive operation becz reading data from the disk is always slower than reading it from the memory
    # So when django evaluates this query & gets the data from the database it is goona store soomewhere in memory called queryset cached
    # So 2nd time when we convert this queryset into list django is not gonna evalauate this query again, it's not gonna go to the db
    # It's gonna read the query from the queryset cached
    queryset = Product.objects.all()
    # same thing happens if you access an individual element from this queryset
    # Again Django is going to read this object from the queryset cached
    queryset[0]

    # One thing you need to know:
    # Caching happens only if we evaluate the entire queryset 1st
    # eg => first we are evaluating the entire queryset first & then accessing the invidual element 
    queryset = Product.objects.all()
    list(queryset)
    queryset[0]

    # In contrast if you access an individual element first and then convert our queryset into list, you will end up with 2 
    # queries sent to db
    queryset = Product.objects.all()
    queryset[0]
    list(queryset)

    return render(request, 'hello.html', {'result': list(queryset)})





    


    




















