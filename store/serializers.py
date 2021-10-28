from decimal import Decimal
from django.db import transaction
from rest_framework import serializers
from .models import Product, Collection, Review, Cart, CartItem, Customer, Order, OrderItem
from .signals import order_created


class CollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Collection
        fields = ['id', 'title', 'product_count']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    product_count = serializers.IntegerField(read_only=True) 

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'slug', 'unit_price', 'price_with_tax', 'collection', 'inventory']
    # id = serializers.IntegerField()
    # title = serializers.CharField(max_length=255)
    # price = serializers.DecimalField(max_digits=6, decimal_places=2, source='unit_price')
    price_with_tax = serializers.SerializerMethodField(method_name='calculate_tax')
    # # collection = serializers.PrimaryKeyRelatedField(
    # #     queryset=Collection.objects.all()
    # # )
    # # collection = serializers.StringRelatedField()
    # # collection = CollectionSerializer()
    # collection = serializers.HyperlinkedRelatedField(
    #     queryset=Collection.objects.all(),
    #     view_name='collection-detail'
    # )

    def calculate_tax(self, product: Product):
        return product.unit_price * Decimal(1.1)

    # def validate(self, data):
    #     if data['password'] != data['conf_password']:
    #         return serializers.ValidationError('Passwords do not match')

    # def create(self, validated_data):
    #     product = Product(**validated_data)
    #     product.other = 123
    #     product.save()
    #     return product
    
    # def update(Self, instance, validated_data):
    #     instance.unit_price = validated_data.get('unit_price') 
    #     instance.save()
    #     return instance

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ['id', 'name', 'description', 'date']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return Review.objects.create(product_id=product_id, **validated_data)

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(Self, cart_item:CartItem):
        return cart_item.product.unit_price * cart_item.quantity

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'total_price']

class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, cart):
        return sum([item.product.unit_price * item.quantity for item in cart.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product found')
        return value



    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id, **self.validated_data)
        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'product_id', 'quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'user_id', 'membership', 'phone', 'birth_date']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, order_item:OrderItem):
        return order_item.product.unit_price * order_item.quantity

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, order:OrderItem):
        return sum([item.product.unit_price * item.quantity for item in order.items.all()])

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'customer', 'payment_status', 'items', 'total_price']

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart with the given ID was found.')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Your cart is empty!')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            customer_id = Customer.objects.get(user_id=self.context['user_id'])
            order = Order.objects.create(customer_id=customer_id.id)

            cart_item = CartItem.objects \
                .select_related('product') \
                    .filter(cart_id=cart_id)
            
            order_items = [
                OrderItem(
                    unit_price=item.product.unit_price, 
                    product=item.product, 
                    order=order, 
                    quantity=item.quantity
                ) for item in cart_item
            ]
            OrderItem.objects.bulk_create(order_items)

            Cart.objects.filter(pk=cart_id).delete()

            order_created.send_robust(self.__class__, order=order)
            return order



