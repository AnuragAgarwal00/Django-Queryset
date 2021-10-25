from django.urls import path
from . import views
from rest_framework_nested import routers


router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('collection', views.CollectionViewSet, basename='cart')
router.register('cart', views.CartViewSet)

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register('reviews', views.ReviewViewSet, basename='product-reviews')

cart_item_router = routers.NestedDefaultRouter(router, 'cart', lookup='cart')
cart_item_router.register('items', views.CartItemViewSet, basename='cart-items')

urlpatterns = router.urls + product_router.urls + cart_item_router.urls
