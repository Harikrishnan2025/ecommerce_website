from django.urls import path
from .views import CreateReviewView, ProductReviewListView, DeleteReviewView

urlpatterns = [
    path('add/<int:product_id>/', CreateReviewView.as_view(), name='add-review'),
    path('product/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('delete/<int:product_id>/', DeleteReviewView.as_view(), name='delete-review'),
]