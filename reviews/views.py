from rest_framework import generics, permissions
from rest_framework.exceptions import PermissionDenied
from .models import Review
from .serializers import ReviewSerializer
from orders.models import Order,OrderItem
from django.shortcuts import get_object_or_404
from products.models import Product
from rest_framework.exceptions import ValidationError
from django.shortcuts import render
from django.shortcuts import redirect


def add_review_redirect(request):
    product_id = request.GET.get('product_id')
    if product_id:
        return redirect('add-review', product_id=product_id)
    return redirect('home') 
class CreateReviewView(generics.CreateAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Review.objects.all()
    def perform_create(self, serializer):
        user = self.request.user
        product_id = self.kwargs.get('product_id')
        product = get_object_or_404(Product, id=product_id)

        has_ordered = Order.objects.filter(user=user, items__product=product).exists()
        if not has_ordered:
            raise PermissionDenied("You can only review products you have purchased.")
        if Review.objects.filter(user=user, product=product).exists():
            raise ValidationError("You have already reviewed this product.")
        serializer.save(user=user, product=product)

class ProductReviewListView(generics.ListAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return Review.objects.filter(product_id=product_id)

class DeleteReviewView(generics.DestroyAPIView):
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'product_id'
    lookup_url_kwarg = 'product_id'

    def get_queryset(self):
         return Review.objects.filter(user=self.request.user)