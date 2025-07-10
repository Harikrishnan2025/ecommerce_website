from django.urls import path
from .views import CreateReviewView, ProductReviewListView, DeleteReviewView,add_review_redirect

urlpatterns = [
    path('review/', add_review_redirect, name='add-review-dynamic'),
    path('add/<int:product_id>/', CreateReviewView.as_view(), name='add-review'),
    path('product/<int:product_id>/', ProductReviewListView.as_view(), name='product-reviews'),
    path('add/<int:product_id>/delete/', DeleteReviewView.as_view(), name='delete-review'),
]