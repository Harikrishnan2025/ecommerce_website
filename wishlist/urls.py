from django.urls import path
from .views import AddToWishlistView,WishListView,RemoveFromWishlistView
urlpatterns = [
    path('list/', WishListView.as_view(), name='wishlist'),
    path('add/<int:product_id>/', AddToWishlistView.as_view(), name='addwishlist'),
    path('remove/<int:product_id>/', RemoveFromWishlistView.as_view(), name='remove-from-wishlist'),

]

