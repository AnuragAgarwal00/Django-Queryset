from django.db import models


class Collection(models.Model):
    title = models.CharField(max_length=255)
    featured_product = models.ForeignKey("Product", on_delete=models.SET_NULL, null=True, related_name="+")

    def __str__(self):
        return self.title

    class Meta:
        # SORT THE COLLECTION BY THEIR TITLE IN ASC IN ADMIN PANEL
        ordering = ['title']

class Promotion(models.Model):
    description = models.CharField(max_length=255)
    discount = models.FloatField()

class Product(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)
    collection = models.ForeignKey(Collection, on_delete=models.PROTECT)
    promotions = models.ManyToManyField(Promotion)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
    


class Customer(models.Model):
    MEMBERSHIP_BRONZE = "B"
    MEMBERSHIP_SILVER = "S"
    MEMBERSHIP_GOLD = "G"

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONZE, 'Bronze'),
        (MEMBERSHIP_SILVER, 'Silver'),
        (MEMBERSHIP_GOLD, 'Gold'),
    ]
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=255)
    birth_date = models.DateField(null=True)
    membership = models.CharField(max_length=1, default=MEMBERSHIP_BRONZE)


    def __str__(self):
        return f'{self.first_name} + {self.last_name}'
    

    class Meta:
        db_table = 'store_customer'
        indexes = [
            models.Index(fields=['first_name', 'last_name'])
        ]
        ordering = ['first_name', 'last_name']


class Order(models.Model):
    PAYEMNT_STATUS_PENDING = 'P'
    PAYEMNT_STATUS_COMPLETED = 'C'
    PAYEMNT_STATUS_FAILED = 'F'

    PAYMENT_CHOICES = [
        (PAYEMNT_STATUS_PENDING, "Pending"),
        (PAYEMNT_STATUS_COMPLETED, "Completed"),
        (PAYEMNT_STATUS_FAILED, "Failed"),
    ]
    placed_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=1, default=PAYEMNT_STATUS_PENDING)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.PROTECT)
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=6, decimal_places=2)

    
    


class Address(models.Model):
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    zip = models.CharField(max_length=255)
    # customer = models.OneToOneFeild(Customer, on_delete=models.CASCADE, primary_key=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


class Cart(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

