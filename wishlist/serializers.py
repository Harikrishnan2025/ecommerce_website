from rest_framework import serializers
from .models import Wishlist
from products.models import Product
from django.shortcuts import get_object_or_404

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'price']  

class WishlistItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created']

class AddWishListSerialiZer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = []

    def validate(self, attrs):
        user = self.context['request'].user
        product_id = self.context.get('product_id')

        if not product_id:
            raise serializers.ValidationError("Product ID is required.")

        product = get_object_or_404(Product, id=product_id)

        if Wishlist.objects.filter(user=user, product=product).exists():
            raise serializers.ValidationError("This product is already in your wishlist.")

        self.context['product'] = product
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        product = self.context['product']
        return Wishlist.objects.create(user=user, product=product)