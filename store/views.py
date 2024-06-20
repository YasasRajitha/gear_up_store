from django.db.models.functions import Concat,Cast
from django.db.models import Value,F
from django.conf import settings
from django.forms import CharField
from django.shortcuts import get_object_or_404
from django.core.mail import send_mail,mail_admins,BadHeaderError
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,RetrieveModelMixin,DestroyModelMixin
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework import status

from .models import Customer, Order,\
                    Product,\
                    Cart,\
                    CartItem
from .serializers import    CustomerSerializer, \
                            OrderSerializer, \
                            ProductSerializer,\
                            CartSerializer, \
                            CartItemSerializer, \
                            AddCartItemSerializer,\
                            UpdateCartItemSerializer

class ProductViewSet(ModelViewSet):

    queryset = Product.objects.all().order_by('id')
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['title','description']
    ordering_fields = ['unit_price','last_update']

    def get_serializer_context(self):
        return {'request': self.request}

    def destroy(self, request, *args, **kwargs):
        product = get_object_or_404(Product,pk=kwargs['pk'])
        if product.orderitems.count() > 0:
            return Response({'error' : 'Product cannot be deleted because it is associated with an order item.'}
                            , status=status.HTTP_405_METHOD_NOT_ALLOWED)

        return super().destroy(request, *args, **kwargs)
    
class CartViewSet(ModelViewSet):
    # queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

    def get_queryset(self):
        print(self.kwargs)

        if self.request.user.is_staff:
            return Cart.objects.prefetch_related('items__product').all()

        return Cart.objects.filter(customer_id=self.kwargs['customer_pk'])
    
    def get_serializer_context(self):
        print(self.kwargs)
        return {'customerid' : self.kwargs['customer_pk']}

class CartItemViewSet(ModelViewSet):

    permission_classes = [IsAuthenticated]

    http_method_names = ['get','post','patch','delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer 

    def get_serializer_context(self):
        return {'cart_id' : self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects.select_related('product').filter(cart_id=self.kwargs['cart_pk'])
    
class CustomerViewSet(ModelViewSet):
    # queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return Customer.objects.all()
        return Customer.objects.filter(user_id=self.request.user.id)

    # def get_serializer_context(self):
    #     return {'user_id' : self.request.user.id}

    # @action(detail=True)
    # def history(self, request, pk):
    #     return Response('ok')

    # @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    # def me(self, request):
    #     (customer,created) = Customer.objects.get_or_create(user_id=request.user.id)
    #     if request.method == 'GET':
    #         serializer = CustomerSerializer(customer)
    #         return Response(serializer.data)
    #     elif request.method == 'PUT':
    #         serializer = CustomerSerializer(customer, data=request.data)
    #         serializer.is_valid(raise_exception=True)
    #         serializer.save()
    #         return Response(serializer.data)


class OrderViewSet(ModelViewSet):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # cart_list = CartItem.objects.select_related('cart__customer').values
        # cart_list_ann = cart_list.annotate(item_details = Concat(F('product'),Value('-'),F('product__title'),Value(' x '),Cast(F('quantity'),CharField()),output_field=CharField()))
        # print(cart_list_ann)
        # return Order.objects.select_related('customer__cart','customer__cart__items').values('id','delivery_address','payment_status','placed_at','customer_id','customer__cart').filter(customer_id=self.kwargs['nested_1_pk'])
        return Order.objects.filter(customer_id=self.kwargs['nested_1_pk'])

    def get_serializer_context(self):
        print(self.kwargs)
        return {'customer_id' : self.kwargs['nested_1_pk']}

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
    
        if response.status_code == status.HTTP_201_CREATED:
            order = response.data
            customer_email = request.user.email
            subject = 'Order Confirmation'
            message = f"Thanx for Ur order, {request.user.username}!\n\nOrder ID:{order['id']}\nPlaced at:{order['placed_at']}\nDelivery Address:{order['delivery_address']}\nItems:{order['items']}"
            from_email = settings.DEFAULT_FROM_EMAIL
            recipient_list = [customer_email]

            try:
                send_mail(subject,message,from_email,recipient_list,fail_silently=False)
            except BadHeaderError:
                pass

        return response
    