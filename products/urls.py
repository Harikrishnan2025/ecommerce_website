from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (productListView,ProductDetailView,
                    DeleteProductView,CategoryView,ProductCreateView,
                    ProductUpdateView,product_form_view,product_update_form)

router = DefaultRouter()
router.register(r'category', CategoryView, basename='category')

urlpatterns = [
    path('', include(router.urls)),
    path('product/',productListView.as_view(),name="prod_list"),
    path('product/delete/<int:pk>/',DeleteProductView.as_view(),name="prod_delete"),
    path('product/<int:pk>/',ProductDetailView.as_view(),name="prod_update"),
    path('product/<int:pk>/edit/', product_update_form, name='product_update_form'),
    path('api/product/<int:pk>/update/', ProductUpdateView.as_view(), name='api_product_update'),
    path('create/', product_form_view, name='product_form'),
    path('api/create/', ProductCreateView.as_view(), name='api_create_product'),
]

