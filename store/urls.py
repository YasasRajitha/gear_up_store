from rest_framework_nested import routers
from . import views
from pprint import pprint

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
router.register('carts',views.CartViewSet, basename='carts')
router.register('customers',views.CustomerViewSet, basename='customers')

# carts_router = routers.NestedDefaultRouter(router, 'customers', lookup='cart')
# carts_router.register('carts', views.CartViewSet, basename='customer-carts')

cart_items_router = routers.NestedDefaultRouter(router, 'carts', lookup='item')
cart_items_router.register('items', views.CartItemViewSet, basename='cart-items')

orders_router = routers.NestedDefaultRouter(router, 'customers', 'customer')
orders_router.register('orders',views.OrderViewSet, basename='customer-orders')

urlpatterns = router.urls +  cart_items_router.urls + orders_router.urls