from rest_framework import serializers
from .models import Product, Category, ProductImage
from reviews.serializers import ReviewDisplaySerializer

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

class ProductListSerializer(serializers.ModelSerializer):
    first_image=serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'first_image','created_at','category']

    def get_first_image(self,obj):
        first_img = obj.images.first()
        if first_img:
            return first_img.image.url
        return None

class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all()
    )
    images = ProductImageSerializer(many=True, read_only=True)
    upload_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'category', 'images', 'quantity','upload_images']
    def create(self, validated_data):
        images_data = validated_data.pop('upload_images', [])
        product = Product.objects.create(**validated_data)
        for image in images_data:
            ProductImage.objects.create(product=product, image=image)
        return product
    def update(self, instance, validated_data):
        
        images_data = validated_data.pop('upload_images',None)

       
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if 'upload_images' in self.initial_data and images_data:
            instance.images.all().delete()
            for image in images_data:
                ProductImage.objects.create(product=instance, image=image)
        return instance

class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer()
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)
    review_count = serializers.IntegerField(read_only=True)
    reviews = ReviewDisplaySerializer(many=True, read_only=True)

    class Meta:
        model = Product
        fields = ['id', 'name', 'description', 'price', 'quantity','category','images','average_rating', 'review_count', 'reviews']