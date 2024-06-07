from django.db.models.aggregates import Count
from decimal import Decimal
from rest_framework import serializers
from .models import Customer, Order,Product,Cart,CartItem

class ProductSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'title', 'unit_price', 'description', 'slug', 'inventory']

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','title','unit_price']

    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

class CartItemSerializer(serializers.ModelSerializer):

    product = SimpleProductSerializer()

    class Meta:
        model = CartItem
        fields = ['id','product','quantity','total_price']

    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.unit_price

    
class AddCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    
    def validate_product_id(self, value):
        if not Product.objects.filter(pk=value).exists():
            raise serializers.ValidationError('No product match with the given ID')
        return value
    
    def save(self):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']
        
        try:
            cart_item = CartItem.objects.get(cart_id=cart_id,product_id=product_id)
            cart_item.quantity += quantity
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(cart_id=cart_id,**self.validated_data)

        return self.instance


    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']

class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']

class CustomerSerializer(serializers.ModelSerializer):

    # user_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Customer
        fields = ['id', 'user', 'phone', 'birth_date']

    # def create(self, validated_data):
    #     user_id = self.context['user_id']
    #     return Customer.objects.create(user_id=user_id,**validated_data)

class OrderSerializer(serializers.ModelSerializer):
    placed_at = serializers.DateTimeField(read_only=True)
    customer_id = serializers.IntegerField(read_only=True)
    items = CartItemSerializer(read_only=True,many=True)
    
    class Meta:
        model = Order
        fields = ['id','placed_at','payment_status','customer_id','items','delivery_address']

    def create(self, validated_data):
        customer_id = self.context['customer_id']

        return Order.objects.create(customer_id=customer_id,**validated_data)

class CartSerializer(serializers.ModelSerializer):

    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True,read_only=True)
    # customer_id = serializers.IntegerField()
    total_price = serializers.SerializerMethodField(method_name='get_total_price')

    def get_total_price(self, cart:Cart):
        return sum([item.quantity * item.product.unit_price for item in cart.items.all()])
    
    def create(self, validated_data):
        customer_id = self.context['customerid']

        return Cart.objects.create(customer_id=customer_id,**validated_data)
    
    class Meta:
        model = Cart
        fields = ['id','items','customer_id','total_price']