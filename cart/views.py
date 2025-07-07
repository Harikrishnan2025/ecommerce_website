from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Cart,CartItem
from .serializers import CartItemSerializer,CartItemQuantityUpdateSerializer
from rest_framework import generics,permissions,status

class CartItemListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self,request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        items = CartItem.objects.filter(cart=cart)
        serializer = CartItemSerializer(items, many=True)
        total = sum(item.product.price * item.quantity for item in items)
        return Response ({'items': serializer.data,'cart_total': total
        })
    
    def post(self,request):
        cart, _ = Cart.objects.get_or_create(user=request.user)
        serializer = CartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.validated_data['product']
        quantity = serializer.validated_data['quantity']
        if quantity <= 0:
            return Response(
            {"error": "Quantity must be greater than zero."},
            status=status.HTTP_400_BAD_REQUEST
             )
        cart_item_qs = CartItem.objects.filter(cart=cart, product=product).first() 
        existing_quantity = cart_item_qs.quantity if cart_item_qs else 0       
        new_total_quantity = existing_quantity + quantity

        if new_total_quantity > product.quantity:
            available_qty = product.quantity - existing_quantity
            if available_qty <= 0:
                return Response(
                {"error": "Product is out of stock."},
                status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {"error": f"Only {available_qty} item(s) left in stock."},
                status=status.HTTP_400_BAD_REQUEST
                )
        if cart_item_qs:
            cart_item_qs.quantity = new_total_quantity
            cart_item_qs.save()
            cart_item = cart_item_qs
        else:
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)

        return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)



class CartItemDeleteView(generics.DestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    def get_queryset(self):
        return CartItem.objects.filter(cart__user=self.request.user)

class CartItemUpdate(generics.UpdateAPIView):
    serializer_class = CartItemQuantityUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        cart, _ = Cart.objects.get_or_create(user=self.request.user)
        return CartItem.objects.filter(cart=cart)


