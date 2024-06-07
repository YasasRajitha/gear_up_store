from rest_framework_nested import routers
from . import views
from pprint import pprint

router = routers.DefaultRouter()
router.register('products', views.ProductViewSet, basename='products')
# router.register('carts',views.CartViewSet, basename='carts')
router.register('customers',views.CustomerViewSet, basename='customers')

carts_router = routers.NestedDefaultRouter(router, 'customers', lookup='customer')
carts_router.register('carts', views.CartViewSet, basename='customer-carts')

cartitems_router = routers.NestedDefaultRouter(carts_router, 'carts', lookup='cart')
cartitems_router.register('items', views.CartItemViewSet, basename='cart-items')

orders_router = routers.NestedDefaultRouter(router, 'customers', 'customer')
orders_router.register('orders',views.OrderViewSet, basename='customer-orders')

urlpatterns = router.urls + carts_router.urls + cartitems_router.urls + orders_router.urls