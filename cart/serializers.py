from rest_framework import serializers
from .models import CartItem
from products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source='product.name')
    product_price = serializers.ReadOnlyField(source='product.price')
    total_price = serializers.SerializerMethodField()
    first_image=serializers.SerializerMethodField()

    product = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), required=True)
    quantity = serializers.IntegerField(min_value=1, required=True)

    class Meta:
        model = CartItem
        fields = ['id','first_image','product', 'product_name', 'product_price', 'quantity','total_price']

    def get_total_price(self, obj):
        return obj.product.price * obj.quantity
    def get_first_image(self,obj):
        first_img = obj.product.images.first()
        if first_img:
            return first_img.image.url
        return None


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

