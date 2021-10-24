from rest_framework import serializers
from .models import Product, Collection, Review

from decimal import Decimal

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
