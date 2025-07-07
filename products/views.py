from django.shortcuts import render
from .models import Product,Category,ProductImage
from .serializers import CategorySerializer,ProductImageSerializer,ProductCreateUpdateSerializer,ProductListSerializer,ProductDetailSerializer
from rest_framework import viewsets,generics, filters,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework import status

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin')


class productListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    # filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description','category__name']
    ordering_fields = ['price', 'created_at']
    filterset_fields = ['category',]

class CreateProductView(generics.CreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

class UpdateProductView(generics.UpdateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductCreateUpdateSerializer
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all()
    serializer_class= ProductDetailSerializer
    def get_queryset(self):
        return Product.objects.annotate(
            average_rating=Avg('reviews__rating'),
            review_count=Count('reviews')
        )

class DeleteProductView(generics.DestroyAPIView):
    queryset = Product.objects.all()
    serializer_class= ProductDetailSerializer
    permission_classes = [IsAdminUser]
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]
    
