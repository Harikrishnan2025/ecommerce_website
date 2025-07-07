from rest_framework import serializers
from .models import CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    total_price = serializers.SerializerMethodField()


    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_name', 'product_price', 'quantity','total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity


class CartItemQuantityUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']
    def validate_quantity(self,value):
        product = self.instance.product
        if value > product.quantity:
            raise serializers.ValidationError(
                f"Only {product.quantity} items are available in stock."
            )
        return value

