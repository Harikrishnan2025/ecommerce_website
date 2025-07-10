from django.urls import path
from .views import CartItemListCreateView,CartItemUpdate,CartItemDeleteView

urlpatterns = [
    path('items/', CartItemListCreateView.as_view(), name='cart_items'),
    path('items/<int:pk>/update/', CartItemUpdate.as_view(), name='cart_item_update'),
    path('items/<int:pk>/', CartItemDeleteView.as_view(), name='cart_item_delete'),

]
