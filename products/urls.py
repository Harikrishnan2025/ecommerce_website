from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import productListView,CreateProductView,UpdateProductView,ProductDetailView,DeleteProductView,CategoryView

router = DefaultRouter()
router.register(r'category', CategoryView, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('product/',productListView.as_view(),name="prod_list"),
    path('create/',CreateProductView.as_view(),name="prod_create"),
    path('product/delete/<int:pk>/',DeleteProductView.as_view(),name="prod_delete"),
    path('update/<int:pk>/',UpdateProductView.as_view(),name="prod_update"),
    path('product/<int:pk>/',ProductDetailView.as_view(),name="prod_update"),
]
