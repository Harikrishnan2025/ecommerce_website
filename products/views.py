from django.shortcuts import render
from .models import Product,Category,ProductImage
from .serializers import CategorySerializer,ProductImageSerializer,ProductCreateUpdateSerializer,ProductListSerializer,ProductDetailSerializer
from rest_framework import viewsets,generics, filters,permissions
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.template.response import TemplateResponse
from rest_framework.views import APIView
from django.shortcuts import redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test

@login_required
@user_passes_test(lambda u: u.is_staff)
def product_form_view(request):
    categories = Category.objects.all()
    return render(request, 'create_product.html', {'categories': categories})

def product_update_form(request, pk):
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all()
    return render(request, 'update_product.html', {
        'product': product,
        'categories': categories
    })

class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_staff or request.user.role == 'admin')

class IsAdminOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True  
        return request.user and request.user.is_staff  

class productListView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    search_fields = ['name', 'description','category__name']
    ordering_fields = ['price', 'created_at']
    filterset_fields = ['category',]


class ProductCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        data = request.data.copy()
        files = request.FILES.getlist('upload_images')
        data.setlist('upload_images', files)

        serializer = ProductCreateUpdateSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class ProductUpdateView(APIView):
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser]
    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        data = request.data.copy()
        files = request.FILES.getlist('upload_images')
        data.setlist('upload_images', files)

        serializer = ProductCreateUpdateSerializer(product, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        # self.perform_destroy(instance)
        instance.delete() 
        return Response(
            {"detail": "Product deleted successfully."},
            status=status.HTTP_204_NO_CONTENT
        )

class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    
