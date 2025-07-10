from rest_framework import serializers
from .models import Order,OrderItem
from cart.models import Cart
from rest_framework.exceptions import ValidationError
from django.db import transaction

class CreateOrderSerializer(serializers.ModelSerializer):
    invoice_pdf_url = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_number', 'full_name', 'address', 'payment_method', 'total_price', 'invoice_pdf_url']
        read_only_fields = ['id', 'order_number', 'total_price', 'invoice_pdf_url']

    def get_invoice_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.invoice_pdf and request:
            return request.build_absolute_uri(obj.invoice_pdf.url)
        return None
    
class userOrdeItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    class Meta:
        model =OrderItem
        fields = ['product_name','quantity','price']
class UserOrderListSerializer(serializers.ModelSerializer):
    items = userOrdeItemSerializer(many=True,read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    invoice_pdf_url = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['order_number','full_name','address','total_price','payment_method','status','items','created_at','phone_number','invoice_pdf_url']
    def get_invoice_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.invoice_pdf and request:
            return request.build_absolute_uri(obj.invoice_pdf.url)
        return None
class UpdatrOrderStatusSerializer(serializers.ModelSerializer):
    # status = serializers.ChoiceField(choices=Order.ORDER_STATUS_CHOICES)

    class Meta:
        model = Order
        fields = ['status','payment_method']

class AdminUserOrderListSerializer(serializers.ModelSerializer):
    items = userOrdeItemSerializer(many=True,read_only=True)
    phone_number = serializers.CharField(source='user.phone_number', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    email=serializers.CharField(source='user.email', read_only=True)
    invoice_pdf_url = serializers.SerializerMethodField()
    class Meta:
        model = Order
        fields = ['user_name','email','order_number','address','total_price','payment_method','status','items','created_at','phone_number','invoice_pdf_url']
    def get_invoice_pdf_url(self, obj):
        request = self.context.get('request')
        if obj.invoice_pdf and request:
            return request.build_absolute_uri(obj.invoice_pdf.url)
        return None
