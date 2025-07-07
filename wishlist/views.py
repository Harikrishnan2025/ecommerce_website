from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Wishlist
from products.models import Product
from .serializers import AddWishListSerialiZer,WishlistItemSerializer

class WishListView(generics.ListAPIView):
    serializer_class = WishlistItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')

class AddToWishlistView(generics.CreateAPIView):
    queryset = Wishlist.objects.all()
    serializer_class = AddWishListSerialiZer
    permission_classes = [permissions.IsAuthenticated]
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['product_id'] = self.kwargs.get('product_id')
        return context
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data={}) 
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Added to wishlist"}, status=status.HTTP_201_CREATED)
    
class RemoveFromWishlistView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, *args, **kwargs):
        product_id = self.kwargs.get('product_id')
        wishlist_item = Wishlist.objects.filter(user=request.user, product_id=product_id).first()

        if wishlist_item:
            wishlist_item.delete()
            return Response({"detail": "Product removed from wishlist."}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "Product not found in wishlist."}, status=status.HTTP_404_NOT_FOUND)