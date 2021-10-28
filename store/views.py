from django.shortcuts import render
from django.http import HttpResponse
from django.db.models.aggregates import Count

from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import api_view
from rest_framework.response import Response 
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, DjangoModelPermissions
from rest_framework.views import APIView
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin

from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer, Order
from .filters import ProductFilterSet
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, FullDjangoModelPermissions
from .serializers import (ProductSerializer, 
                          CollectionSerializer, 
                          ReviewSerializer, 
                          CartSerializer,
                           CartItemSerializer,
                           AddCartItemSerializer,
                           UpdateCartItemSerializer,
                           CustomerSerializer,
                           OrderSerializer,
                           CreateOrderSerializer,
                           UpdateOrderSerializer)

class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    # filterset_fields = ['collection_id']
    filterset_class = ProductFilterSet
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update ']

    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = Product.objects.filter(collection_id=collection_id)
    #     return queryset

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        super().destroy(request, *args, **kwargs)


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def delete(self, request, pk):
        collection = get_object_or_404(Collection, pk=pk)
        if collection.products.count > 0:
            return Response({'error': 'Collection cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProductListAPIView(ListCreateAPIView):
    # queryset = Product.objects.select_related('collection').all()
    # serializer_class = ProductSerializer
    def get_queryset(self):
        return Product.objects.select_related('collection').all()
    
    def get_serializer_class(self):
        return ProductSerializer
    
    def get_serializer_context(self):
        return {'request': self.request}

class ProductList(APIView):
    def get(self, request):
        product_queryset = Product.objects.select_related('collection').all()
        serializer = ProductSerializer(product_queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ProductDetailGenericView(RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def delete(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        if product.order_items.count() > 0:
            return Response({'error': 'Product cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
class ProductDetail(APIView):
    def get(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    def put(self, request, id):
        product = get_object_or_404(Product, pk=id)
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, id):
        product = get_object_or_404(Product, pk=id)
        if product.order_items.count() > 0:
            return Response({'error': 'Product cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        product_queryset = Product.objects.select_related('collection').all()
        serializer = ProductSerializer(product_queryset, many=True, context={'request': request})
        return Response(serializer.data)
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

@api_view(['GET', 'PUT', 'DELETE'])
def product_detail(request, id):
    product = get_object_or_404(Product, pk=id)
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if product.order_items.count() > 0:
            return Response({'error': 'Product cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionDetailGenericView(RetrieveUpdateDestroyAPIView):
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer

    def delete(self, request, pk):
        collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=pk)
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)





@api_view(['GET', 'PUT', 'DELETE'])
def collection_detail(request, pk):
    collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=pk)
    if request.method == "GET":
        serializer = CollectionSerializer(collection)
        return Response(serializer.data)
    elif request.method == "PUT":
        serializer = CollectionSerializer(collection, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    elif request.method == 'DELETE':
        if collection.products.count() > 0:
            return Response({'error': 'Collection cannot be deleted'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class CollectionListAPIView(ListCreateAPIView):
    def get_queryset(self):
        return Collection.objects.annotate(product_count=Count('products'))

    def get_serializer_class(self):
        return CollectionSerializer
         

@api_view(['GET', 'POST'])
def collection_list(request):
    if request.method == "GET":
        collection_queryset = Collection.objects.annotate(product_count=Count('products'))
        serializer = CollectionSerializer(collection_queryset, many=True)
        return Response(serializer.data)
    elif request.method == "POST":
        serializer = CollectionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product=self.kwargs['product_pk'])
    

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}

class CartViewSet(CreateModelMixin, 
                  RetrieveModelMixin, 
                  DestroyModelMixin, 
                  GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs.get('cart_pk'))

class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    # what if you want to have differnent permission for differnet actions like Create and Retrieve
    # Let's say we want anyone to be able to retrieve a customer object but only authenticated users or admin users 
    # can update a customer object, for that we need to override the method in this viewset

    # def get_permissions(self):
    #     if self.request.method == 'GET':
    #         return [AllowAny()]
    #     return [IsAuthenticated()]


    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated])
    def me(self, request):
        customer = Customer.objects.get(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']
    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]


    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data)


    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        elif self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Order.objects.all()
        customer_id = Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id.id)

    
    


